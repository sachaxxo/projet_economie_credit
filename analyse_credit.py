# Première analyse reproductible : exécuter depuis le dossier du projet.
# Voir README.md et le notebook pour les interprétations.
from pathlib import Path
import json, hashlib, platform
import numpy as np
import pandas as pd
import sklearn
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
 roc_auc_score, average_precision_score, confusion_matrix, PrecisionRecallDisplay)
ROOT=Path.cwd()
if ROOT.name!='projet_economie_credit': ROOT=ROOT/'projet_economie_credit'
plt.rcParams.update({'figure.dpi':140,'axes.spines.top':False,'axes.spines.right':False,'font.size':10})
source=ROOT/'data'/'default of credit card clients.xls'
df=pd.read_excel(source,header=1).rename(columns={'default payment next month':'DEFAULT'})
df.to_csv(ROOT/'data'/'credit_clients.csv',index=False)
print('Dimensions :',df.shape)
print('Valeurs manquantes :',int(df.isna().sum().sum()))
print('Identifiants uniques :',df.ID.nunique())
print('Doublons exacts hors ID :',int(df.drop(columns='ID').duplicated().sum()))
print('Effectifs de la cible :',df.DEFAULT.value_counts().sort_index().to_dict())
print('Taux de défaut :',round(100*df.DEFAULT.mean(),2),'%')
print('Codes EDUCATION :',df.EDUCATION.value_counts().sort_index().to_dict())
print('Codes MARRIAGE :',df.MARRIAGE.value_counts().sort_index().to_dict())
print('Codes PAY_0 :',df.PAY_0.value_counts().sort_index().to_dict())
df.describe().to_csv(ROOT/'statistiques_descriptives.csv')

fig,ax=plt.subplots(figsize=(6.3,3.5))
counts=df.DEFAULT.value_counts().sort_index()
ax.bar(['Sans défaut','Défaut'],counts,color=['#2563eb','#d97706'])
for i,v in enumerate(counts): ax.text(i,v+350,f'{v:,} ({v/len(df):.2%})',ha='center')
ax.set(ylabel='Nombre de clients',title='Une classe de défaut minoritaire',ylim=(0,27000))
fig.tight_layout();fig.savefig(ROOT/'figures'/'01_classes.png');plt.close(fig)
print('Un modèle qui prédit toujours « sans défaut » atteint',f'{1-df.DEFAULT.mean():.2%}',"d'exactitude, mais ne détecte aucun défaut.")

eda=df.groupby('PAY_0').DEFAULT.agg(['size','mean'])
print(eda.round(4).to_string())
fig,ax=plt.subplots(figsize=(7,3.8))
ax.bar(eda.index.astype(str),100*eda['mean'],color='#2563eb')
ax.set(xlabel='Code du statut de remboursement en septembre (PAY_0)',ylabel='Taux de défaut le mois suivant (%)',title='Association entre statut récent et défaut futur')
for i,(_,r) in enumerate(eda.iterrows()): ax.text(i,100*r['mean']+1,f"n={int(r['size'])}",ha='center',fontsize=8)
ax.set_ylim(0,110);fig.tight_layout();fig.savefig(ROOT/'figures'/'02_statut.png');plt.close(fig)

fig,ax=plt.subplots(figsize=(6.3,3.5))
ax.boxplot([df.loc[df.DEFAULT==k,'LIMIT_BAL'] for k in [0,1]],tick_labels=['Sans défaut','Défaut'],showfliers=False)
ax.set(ylabel='Plafond de crédit (dollars taïwanais)',title='Plafond de crédit selon le défaut observé')
fig.tight_layout();fig.savefig(ROOT/'figures'/'03_plafond.png');plt.close(fig)
print(df.groupby('DEFAULT').LIMIT_BAL.agg(['mean','median']).round(2).to_string())

X=df.drop(columns=['ID','DEFAULT']).copy();y=df.DEFAULT.copy()
X['EDUCATION']=X.EDUCATION.where(X.EDUCATION.isin([1,2,3,4]),0)
groups=pd.util.hash_pandas_object(X,index=False).astype(str)
fold=np.full(len(df),-1)
for k,(_,idx) in enumerate(StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=42).split(X,y,groups)):
 fold[idx]=k
train_idx=np.flatnonzero(fold>=2);val_idx=np.flatnonzero(fold==1);test_idx=np.flatnonzero(fold==0)
assert not (set(groups.iloc[train_idx]) & set(groups.iloc[val_idx]))
assert not (set(groups.iloc[train_idx]) & set(groups.iloc[test_idx]))
assert not (set(groups.iloc[val_idx]) & set(groups.iloc[test_idx]))
partition=np.where(fold==0,'test',np.where(fold==1,'validation','apprentissage'))
pd.DataFrame({'ID':df.ID,'partition':partition}).to_csv(ROOT/'partitions.csv',index=False)
print(pd.DataFrame({'partition':partition,'defaut':y}).groupby('partition').agg(n=('defaut','size'),taux_defaut=('defaut','mean')).round(4).to_string())
cat=['SEX','EDUCATION','MARRIAGE','PAY_0','PAY_2','PAY_3','PAY_4','PAY_5','PAY_6']
num=[c for c in X if c not in cat]
def preprocessing():
 return ColumnTransformer([
  ('numeriques',Pipeline([('imputation',SimpleImputer(strategy='median')),('echelle',StandardScaler())]),num),
  ('categories',Pipeline([('imputation',SimpleImputer(strategy='most_frequent')),('encodage',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cat)])
models={
 'Référence majoritaire':DummyClassifier(strategy='most_frequent'),
 'Logit pondéré':LogisticRegression(max_iter=1500,class_weight='balanced',random_state=42),
 'Forêt aléatoire':RandomForestClassifier(n_estimators=100,min_samples_leaf=5,class_weight='balanced_subsample',random_state=42,n_jobs=2)}
Xtr=X.iloc[train_idx];ytr=y.iloc[train_idx];Xval=X.iloc[val_idx];yval=y.iloc[val_idx]
cv=StratifiedGroupKFold(n_splits=3,shuffle=True,random_state=123)
rows=[]; fitted={}
for name,model in models.items():
 pipe=Pipeline([('pretraitement',preprocessing()),('modele',model)])
 ap=cross_val_score(pipe,Xtr,ytr,groups=groups.iloc[train_idx],cv=cv,scoring='average_precision',n_jobs=1)
 pipe.fit(Xtr,ytr); proba=pipe.predict_proba(Xval)[:,1];pred=(proba>=.5).astype(int)
 row={'modele':name,'AP_CV_moyenne':ap.mean(),'AP_CV_ecart_type':ap.std(),
 'AP_validation':average_precision_score(yval,proba),'AUC_ROC':roc_auc_score(yval,proba),
 'accuracy':accuracy_score(yval,pred),'precision':precision_score(yval,pred,zero_division=0),
 'rappel':recall_score(yval,pred),'F1':f1_score(yval,pred),'matrice':confusion_matrix(yval,pred).tolist()}
 rows.append(row);fitted[name]=(pipe,proba,pred)
results=pd.DataFrame(rows)
results.drop(columns='matrice').to_csv(ROOT/'resultats_validation.csv',index=False)
print(results.drop(columns='matrice').round(4).to_string(index=False))
for r in rows: print(r['modele'],'matrice [[VN,FP],[FN,VP]] :',r['matrice'])
(ROOT/'resultats.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False))

fig,ax=plt.subplots(figsize=(6.5,4))
for name,(_,proba,_) in fitted.items():
 PrecisionRecallDisplay.from_predictions(yval,proba,name=name,ax=ax)
ax.axhline(yval.mean(),color='gray',linestyle='--',label='Prévalence validation')
ax.set(xlabel='Rappel des défauts',ylabel='Précision des alertes',title='Premiers modèles — jeu de validation')
ax.legend(fontsize=8);fig.tight_layout();fig.savefig(ROOT/'figures'/'04_precision_rappel.png');plt.close(fig)