# Premier point d’avancement — Projet Machine Learning
**Master MECEN • Florian Mercier • Sacha Isman

## Sujet : économie du crédit et prédiction du défaut de remboursement
**Problématique :** dans quelle mesure l’historique de remboursement et les caractéristiques financières permettent-ils de prédire un défaut le mois suivant ? Les modèles non linéaires apportent-ils un gain par rapport à une régression logistique ?

L’intérêt économique est d’étudier le compromis entre maîtrise du risque de crédit et accès au financement. Les faux négatifs correspondent à des défauts non détectés ; les faux positifs à des clients sans défaut signalés à tort. Ces erreurs n’ont pas le même coût. La base ne permet cependant pas de chiffrer les pertes ni de conclure sur les effets d’un refus de crédit.

## 1. Base identifiée et téléchargée
**Default of Credit Card Clients**, UCI : https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients

La base compte **30 000 clients**, **23 variables explicatives**, un identifiant et une cible binaire. Les historiques de paiement et montants couvrent avril à septembre 2005 à Taïwan ; la cible indique le défaut le mois suivant. Les montants sont exprimés en dollars taïwanais. La cible n’est pas une mesure de fraude.

Fichiers fournis : original XLS et conversion CSV. Acquisition par téléchargement de données ouvertes ; aucun scraping n’a été réalisé.

## 2. Travail effectivement réalisé pour le moment 
- Chargement des données et vérification des types, modalités et valeurs manquantes.
- Analyse du déséquilibre de la cible et de deux associations descriptives.
- Construction de partitions reproductibles et d’un pipeline de prétraitement.
- Estimation de trois premiers modèles et validation croisée à trois plis sur l’apprentissage.
- Évaluation sur une partition de validation ; **aucune performance calculée sur le test**.

## 3. Premiers constats sur les données
**6 636 clients sont en défaut (22,12 %)** et 23 364 ne le sont pas (77,88 %). Une prédiction systématique « sans défaut » serait donc souvent exacte, tout en manquant tous les défauts. L’accuracy seule est insuffisante.

Aucune cellule manquante au sens informatique n’est détectée. Cela ne signifie pas que toutes les modalités sont documentées : EDUCATION présente les codes 0, 5 et 6 hors des quatre catégories décrites par UCI. Ils sont regroupés en catégorie non documentée. MARRIAGE=0 est conservé comme catégorie distincte. Les statuts PAY sont encodés comme catégories, sans inventer le sens des codes -2 et 0 absents de la notice consultée.

Il existe **35 répétitions exactes hors identifiant**. Elles sont conservées car elles ne prouvent pas des erreurs de saisie ; les profils explicatifs identiques sont regroupés dans la même partition pour éviter leur présence de part et d’autre de la séparation.

Le taux de défaut atteint **69,55 %** parmi les clients dont PAY_0 est au moins égal à 2 (3 130 clients), contre **16,59 %** pour les autres (26 870 clients). Un statut d’au moins deux mois de retard est donc associé à un risque supérieur dans cet échantillon. Il ne s’agit pas d’un effet causal.

## 4. Méthode et premières estimations
La partition, construite avec une graine fixe et des groupes de profils identiques, comporte 17,999 observations d’apprentissage, 6,001 de validation et 6,000 de test. Les proportions sont proches de 60/20/20. Les profils identiques restent aussi groupés dans les plis de validation croisée.

L’identifiant est exclu. Les variables numériques sont standardisées ; les catégories sont encodées en indicatrices. Ces transformations sont ajustées sur l’apprentissage uniquement, à l’intérieur du pipeline. Les valeurs extrêmes ne sont pas supprimées arbitrairement.

Les premiers modèles sont une référence majoritaire, un logit pondéré et une forêt aléatoire pondérée de 100 arbres, avec un minimum de 5 observations par feuille. Ces réglages sont initiaux et ne résultent pas d’une optimisation.

**Résultats sur la validation, seuil fixé à 0,5 :**

| Modèle | AP | AUC-ROC | Précision | Rappel des défauts | F1 |
|---|---:|---:|---:|---:|---:|
| Référence majoritaire | 0.221 | 0.500 | 0.000 | 0.000 | 0.000 |
| Logit pondéré | 0.536 | 0.757 | 0.487 | 0.577 | 0.528 |
| Forêt aléatoire | 0.543 | 0.770 | 0.535 | 0.541 | 0.538 |

L’AP (average precision) résume la courbe précision-rappel ; elle est pertinente pour la classe minoritaire. La référence constante a une AP égale à la proportion de défauts en validation.

La forêt obtient ici une AP légèrement supérieure au logit. À 0,5, elle détecte environ 54 % des défauts ; environ 54 % de ses alertes correspondent à des défauts observés. Le logit détecte davantage de défauts mais avec une précision inférieure. Ces résultats illustrent un compromis ; ils ne suffisent pas à établir une supériorité générale. L’écart doit être confirmé et son incertitude étudiée.

## 5. Limites et suite prévue
La base est ancienne, localisée et concerne des détenteurs de carte déjà sélectionnés. Elle ne permet pas de généraliser directement aux emprunteurs français ni d’étudier les demandes refusées. La séparation aléatoire groupée ne constitue pas un test de robustesse temporelle. Les probabilités issues de modèles pondérés devront être vérifiées et éventuellement calibrées.

Prochaines étapes : compléter la littérature récente ; tester un gradient boosting ; régler les hyperparamètres par recherche aléatoire sur l’apprentissage ; examiner la calibration ; construire des ratios financiers ; analyser les erreurs et l’importance par permutation ; comparer les résultats avec et sans variables démographiques. Le seuil sera discuté sur la validation avant une unique évaluation finale sur le test.



## Références et traçabilité
- Yeh, I. (2009). Default of Credit Card Clients. UCI. DOI : 10.24432/C55S3H. Licence CC BY 4.0.
- Yeh, I.-C. et Lien, C.-H. (2009). The comparisons of data mining techniques for the predictive accuracy of probability of default of credit card clients. Expert Systems with Applications, 36(2), 2473–2480. Référence de départ identifiée ; revue bibliographique à approfondir.

