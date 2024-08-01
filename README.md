
# CFB Realignment Visualizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CFB Realignment Visualizer is an interactive web application designed to visualize and analyze actual realignments of college football conferences. This project leverages a backend API that scrapes data from Wikipedia, processes it for various calculations, and presents the data through a React frontend with Leaflet for mapping, Chart.js for data visualization, and Bootstrap for styling.


## Features

- **Interactive Map**: Visualize the geographic distribution of teams within conferences.
- **Data Analysis**: Includes calculations such as the spread of points (similar to k-nearest calculations) and finding geographic centers.
- **Dynamic Charts**: Display various statistics and metrics using Chart.js.
- **Responsive Design**: Built with Bootstrap for a mobile-friendly experience.

## Technologies Used

- **Frontend**:
  - React
  - Leaflet
  - Chart.js
  - Bootstrap

- **Backend**:
  - Python
  - Django
  - BeautifulSoup

- **Data**:
  - Sourced from Wikipedia
  - JSON format for RESTful API responses


## Setup and Installation

### Prerequisites

- Node.js (v14 or higher)
- Python (v3.8 or higher)
- Virtual Environment (recommended)

### Backend Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/EvanJelley/CFBRealignmentVisualizer.git
   cd CFBRealignmentVisualizer/backend
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend server:**

   ```bash
   python app.py
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**

   ```bash
   cd ../frontend
   ```

2. **Install the required packages:**

   ```bash
   npm install
   ```

3. **Start the development server:**

   ```bash
   npm start
   ```

The application should now be running locally on `http://localhost:3000`.

## Usage

- Navigate through different conference alignments.
- Use the interactive map to explore the geographical layout of the teams.
- Analyze data and trends using the provided charts.

## Contributing

We welcome contributions to improve the project. Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Data sourced from Wikipedia
- Leaflet for map visualizations
- Chart.js for data visualization
- Bootstrap for responsive design

## Contact

For any inquiries, please contact [Evan Jelley](mailto:evanjelley@gmail.com).
