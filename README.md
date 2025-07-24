# Hypernasality CNN Detection
### Project Overview
This repository, Hopkins-Project, contains the implementation of a Convolutional Neural Network (CNN) designed to detect hypernasality, a speech disorder characterized by excessive nasal resonance. The project was developed during an internship and includes code for data preprocessing, model training, and an API for inference, along with Docker configurations for deployment. The goal is to provide a foundation for automated hypernasality detection, which can be used in clinical or research settings.
The project is partially complete, with a functional CNN model and basic API endpoints. This README provides instructions for setting up, running, and extending the project for team members to build upon and finalize deployment.

### Features
- **CNN Model**: A trained CNN model for detecting hypernasality from input data (e.g., spectrograms, audio features, or images, depending on implementation).
- **Data Preprocessing**: Scripts to preprocess input data, such as converting audio to spectrograms or handling image inputs.
- **API Endpoints**: A Flask-based (or similar) API for model inference, allowing users to submit data and receive predictions.
- **Docker Support**: Dockerfile and configuration for containerized deployment.

### Unfinished Features (To Be Completed)
- Full validation of the CNN model on a diverse test dataset.
- Integration with a production-ready database for storing predictions and user data.
- Enhanced API endpoints for batch processing or real-time streaming.
- User interface for easier interaction with the model (e.g., a web or desktop frontend).
- Documentation for dataset preparation and model evaluation metrics.

### Project Structure
Hopkins-Project/
├── data/                       # Input data (e.g., spectrograms, audio files)
├── models/                     # Trained CNN model(s) and checkpoints
├── src/                        # Source code
│   ├── preprocess.py          # Data preprocessing scripts
│   ├── train.py              # CNN model training script
│   ├── predict.py            # Inference script
│   ├── app.py                # Flask API (if applicable)
│   └── models/               # CNN model definitions
├── tests/                     # Unit tests (if implemented)
├── Dockerfile                 # Docker configuration
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore file
└── README.md                 # This file


*Note*: The exact structure may vary. Update this section if additional files or folders (e.g., `docker-compose.yml`, `environment.yml`) are included.

### Prerequisites
- Python v3.12 for running the model and API.
- Docker for containerized deployment.
- Conda or pip for managing Python dependencies.
- (Optional) CUDA-enabled GPU for faster model training (ensure NVIDIA drivers are installed).

### Setup Instructions
1. **Clone the Repository**
```bash
git clone https://github.com/Tyler-Abele/Hopkins-Project.git
cd Hopkins-Project
```

2. **Set Up the Python Environment**

Create and activate a Conda environment (or use `venv`):\
```bash
conda create -n hypernasality python=3.12
conda activate hypernasality
```

Install dependencies:
```bash
pip install -r requirements.txt
```


*Note*: If using Conda, you may need an `environment.yml` file. Run `conda env export > environment.yml` to generate one from an existing environment.

3. **Prepare the Data**

Place input data (e.g., audio files, spectrograms) in the `data/` directory.
Run the preprocessing script to prepare data for the CNN:

```bash
python src/preprocess.py
```


Update `preprocess.py` with specific paths or parameters if needed.

4. **Train the Model**

Train the CNN model using:
```bash
python src/train.py
```

Checkpoints and trained models are saved in the `models/` directory.
Adjust hyperparameters in `train.py` (e.g., learning rate, batch size) based on dataset size and performance.

5. **Run the API**

Start the Flask API (if implemented):

```bash
python src/app.py
```


The API will be available at `http://localhost:5000`. Check `app.py` for specific endpoints (e.g., `/predict` for inference).

6. **Run with Docker**

Build the Docker image:

```bash
docker build -t hypernasality-cnn .
```

Run the container:

```bash
docker run -p 5000:5000 hypernasality-cnn
```
The API will be accessible at `http://localhost:5000`. Ensure Docker is installed and running.
*You can change this out to whatever port you want to run the API on*


Update `Dockerfile` or `docker-compose.yml` for custom configurations (e.g., volume mounts for data).

7. **(Optional) Palantir Foundry Setup**

If using Palantir Foundry, sync data from an S3 bucket or other source to a Foundry dataset.
Use Code Workbook to preprocess data or train the model, following the pipeline setup in `src/`.

### API Endpoints
If a Flask API is included, example endpoints might include:
- **POST /predict**: Submit input data (e.g., spectrogram) for hypernasality prediction.
  - Example: `curl -X POST -F "file=@data/sample.png" http://localhost:5000/predict`
- **GET /health**: Check API status.
- Update this section with specific endpoints from `app.py` or other API code.

### How to Contribute
To continue development, team members can focus on the following tasks:

- **Model Improvement**:
  - Validate the CNN on a larger, diverse dataset to improve accuracy.
  - Experiment with different architectures (e.g., deeper CNNs, ResNet) in `src/models/`.
  - Add data augmentation in `preprocess.py` to handle variations in input data.
- **API Enhancements**:
  - Add batch prediction support to the API.
  - Implement authentication for secure access (e.g., JWT).
  - Integrate with a database (e.g., PostgreSQL) for storing predictions.
- **Frontend Development**:
  - Create a web interface using React or a desktop app to visualize predictions.
  - Add support for uploading audio files and displaying results.
- **Testing**:
  - Write unit tests for preprocessing and inference in `tests/`.
  - Use `pytest` to validate model predictions and API endpoints.
- **Deployment**:
  - Deploy the API to a cloud platform (e.g., AWS, Heroku).
  - Optimize the Docker setup for production (e.g., multi-stage builds).
- **Documentation**:
  - Document dataset requirements (e.g., format, size) in a separate `DATASET.md` file.
  - Add API documentation using Swagger or similar tools.

### Known Issues
- The model may overfit if the dataset is small; consider adding negative samples or data augmentation.
- API error handling may need improvement for robustness.
- Docker image size may be large; optimize by removing unnecessary dependencies.
- Palantir Foundry integration (if used) may require specific credentials or setup.

### Contact
For questions, contact Tyler Abele at **tabele@gmail.com**