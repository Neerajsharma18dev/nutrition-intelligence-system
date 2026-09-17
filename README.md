<div align="left">

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

</div>

# 🥗 Nutrition Intelligence System - AI-Powered Dietary Assessment

A clinical-grade, responsive, and explainable health technology platform built to estimate nutritional deficiency risks (Iron, Vitamin D, Vitamin B12, Calcium, Vitamin C) using a 31-dimensional clinical vector, SHAP factor interpretability, and automated 7-day meal planning.

---

## 🎯 Objective

This system bridges the gap between everyday food diary tracking, clinical symptom screening, and laboratory blood reports. By leveraging decoupled Random Forest classification models and SHAP (SHapley Additive exPlanations), it delivers transparent, interpretable deficiency screenings and actionable, restriction-aware dietary recommendations.

---

## 📸 Preview

### Clinical Dashboard Overview
![Clinical Dashboard](imges/Img1.png)

### Authentication & Access Control
![Authentication](imges/Img2.png)

### Patient Health Profile & Dietary Restrictions
![Patient Health Profile](imges/Img3.png)

### Food Diary & Daily Micronutrient Tracker
![Food Diary](imges/Img4.png)

### AI Risk Screening & SHAP Explainability
![AI Analysis](imges/Img5.png)

### Dietary Recommendations & Clinical Suggestions
![Dietary Recommendations](imges/Img6.png)

### Personalised 7-Day Meal Schedule
![7-Day Meal Plan](imges/Img7.png)

---

## ✨ Features

- **Multi-Nutrient Machine Learning Inference:** 5 independent scikit-learn Random Forest classifiers predicting deficiency risks across critical micronutrients.
- **SHAP TreeExplainer Interpretability:** Plain-English decomposition ranking factors that directly elevate or mitigate deficiency risk.
- **31-Column Clinical Feature Vector:** Incorporates patient demographics, 7-day intake percentages against standard RDAs, 12-point clinical symptom scores, and serum blood markers.
- **Dietary Restriction Engine:** Dynamic catalogue filtering matching suggestions against Vegetarian, Vegan, Gluten-Free, and Dairy-Free restrictions.
- **Automated 7-Day Meal Scheduler:** Dynamic generation of daily balanced meal distributions across Breakfast, Lunch, Dinner, and Snacks.
- **Decoupled Three-Tier Architecture:** Service layer containing zero HTTP dependencies, independent ML training pipelines, and a React interface.
- **Modern Responsive Interface:** Fluid, adaptive dashboard layout supporting both wide desktop displays and mobile screen sizes.

---

## 🛠️ Technologies Used

### Frontend
- React 18
- Vite
- Tailwind CSS
- Lucide React (Icons)
- Axios

### Backend & API
- Python 3.11
- FastAPI
- Pydantic v2
- SQLAlchemy ORM
- Uvicorn

### Machine Learning & Data Science
- Scikit-Learn (Pipelines, Imputation, Random Forest Classifiers)
- SHAP (TreeExplainer)
- Pandas & NumPy
- Joblib (Model Serialization)

### Database & Storage
- SQLite
- Structured JSON Storage

---

## 📂 Project Structure

nutrition-intelligence-system/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   ├── init_db.py
│   ├── seed_foods.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/layout/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── tailwind.config.js
├── ml/
│   ├── pipeline/
│   ├── generate_dataset.py
│   ├── train.py
│   └── explain.py
├── data/
├── database/
├── imges/
└── README.md

---

## 🚀 How to Run Locally

### 1. Clone the Repository
git clone [https://github.com/Neerajsharma18dev/nutrition-intelligence-system.git](https://github.com/Neerajsharma18dev/nutrition-intelligence-system.git)

### 2. Navigate to the Project Folder
cd nutrition-intelligence-system

### 3. Setup & Run Backend
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Initialize database schema and seed catalogue
python init_db.py
python seed_foods.py

# Start FastAPI server
python -m uvicorn app.main:app --reload

### 4. Setup & Run Frontend (In a second terminal)
cd frontend
npm install
npm run dev

### 5. Open in Browser
Visit: http://localhost:5173

---

## 👨‍💻 About the Author

Hi, I'm **Neeraj Sharma**! 👋  

I am an **MSc Data Science student** and an **AI & ML Enthusiast**, passionate about solving real-world problems using **Machine Learning** and **Deep Learning**. I enjoy exploring data, building predictive models, and experimenting with modern AI workflows.

- 🎓 **Education:** Pursuing MSc in Data Science
- 💡 **Interests:** Machine Learning, Deep Learning, Data Analytics & Artificial Intelligence
- 🔭 **Current Focus:** Building hands-on ML/DL projects and practical AI solutions
- 🤝 **Open for:** Collaborations on AI/ML projects and research ideas

---
📬 *Feel free to connect, star the repo ⭐, or reach out if you have feedback or suggestions!*

---

## 📬 Connect With Me

- GitHub: [https://github.com/Neerajsharma18dev](https://github.com/Neerajsharma18dev)
- LinkedIn: [https://www.linkedin.com/in/neeraj-sharma-240b13404/](https://www.linkedin.com/in/neeraj-sharma-240b13404/)
- Email: neerajsharma99840@gmail.com

---

## ⭐ Support

If you find this project informative or useful, please consider giving it a star on GitHub!