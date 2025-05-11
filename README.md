# 🧠 Fake News Detection - Big Data Platform

<div align="center">
  <img src="https://i.ibb.co/FxrMqr7/fake-news-icon.png" alt="Fake News Icon" height="100px"/>
  <br>
  <strong>Streaming & Classifying News Articles with Big Data Tools</strong>
</div>

---

## 📘 Contexte du projet

Ce projet a été développé dans le cadre d’un module de **Big Data & Intelligence Artificielle**.
Il s'agit d'une **plateforme de détection de fausses informations** en temps réel, exploitant un flux Kafka, des modèles d’apprentissage automatique, une base de données NoSQL (Cassandra) et un tableau de bord interactif (Flask).

Notre objectif : créer un **système complet de bout en bout**, de l’ingestion de données à la visualisation des prédictions.

---

## 🎯 Objectifs

* 🔁 Traiter des données de news en **streaming temps réel** via Kafka.
* 🧠 Utiliser des modèles **Naive Bayes & SVM** pour prédire les fausses informations.
* 🗃️ Sauvegarder les résultats dans **Cassandra**.
* 📊 Visualiser les métriques dans un **dashboard Flask interactif**.
* ✅ Fournir une **solution complète, modulaire et maintenable**.

---

## ⚙️ Architecture & Technologies

| Composant            | Technologie utilisée           |
| -------------------- | ------------------------------ |
| Data Streaming       | Apache **Kafka**               |
| Prétraitement & ML   | Python · Pandas · Scikit-learn |
| Modèles utilisés     | Naive Bayes · SVM              |
| Base de données      | **Apache Cassandra** (NoSQL)   |
| Frontend Dashboard   | **Flask** + HTML/CSS           |
| Déploiement          | Localhost (ou Docker)          |
| Entraînement modèles | `models/train_models.py`       |

---

## 🧱 Structure du projet

```
FakeNewsDetectionBigData/
├── config/
│   └── settings.py
├── producer.py
├── consumer.py
├── evaluation.py
├── dashboard.py
├── models/
│   ├── train_models.py
│   ├── naive_bayes_model.pkl
│   ├── svm_model.pkl
│   └── tfidf_vectorizer.pkl
├── templates/
│   └── dashboard.html
├── data/
│   └── final_fake_real_news.tsv
├── scripts/
│   └── run_all.bat
├── requirements.txt
└── README.md
```

---

## 🚀 Lancement de la plateforme

### ⚙️ Prérequis

* Python 3.7+
* Kafka & Zookeeper configurés
* Cassandra installé et opérationnel
* Packages : voir `requirements.txt`

### 🧪 Installation & Exécution

```bash
# Créer un environnement virtuel
python -m venv venv
venv\Scripts\activate   # (Windows)

# Installer les dépendances
pip install -r requirements.txt

# Lancer Kafka + Cassandra (si non déjà lancés)

# Lancer tous les scripts automatiquement
scripts\run_all.bat
```

> 📌 Vous pouvez aussi exécuter chaque script individuellement selon votre architecture.

---

## 🖥️ Dashboard Web

Une fois le script `dashboard.py` lancé :

🔗 Accès : [http://127.0.0.1:5000](http://127.0.0.1:5000)

Fonctionnalités :

* 🎯 Prédiction en ligne de texte
* 📊 Affichage de l’accuracy globale et par modèle
* 🧠 Statistiques sur les performances du classifieur

---

## 📑 Dataset utilisé

Fichier : `data/final_fake_real_news.tsv`
Format : TSV avec colonnes `text` et `label`

* `0` → Real news
* `1` → Fake news

---

## 🔐 Sécurité & Fiabilité

* 🔒 Les données sensibles sont configurées dans `config/settings.py`
* 📈 Le pipeline Kafka est résilient aux erreurs
* 🧪 Les prédictions sont validées avant insertion

---

## 📄 Documentation complémentaire

* 🛠 `train_models.py` : script d'entraînement des modèles
* 🗃 `evaluation.py` : calcule et stocke les métriques dans Cassandra
* 📥 `producer.py` : lit le dataset et publie dans Kafka
* 📤 `consumer.py` : reçoit les données, prédit, stocke

---

## 👨‍💻 Réalisé par

**ENIHE Nouhaila**, **OUAHMIDI Lamya** & **Ossama ETTAQAFI (me)**
Étudiants en Master Data Science & IA
Université ENSAJ

---

## 📜 Licence

Ce projet est open source sous la licence MIT.