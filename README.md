# ChatGPT Scraper 🛠️

ChatGPT Scraper is a **Flask-based** application that allows users to extract conversations from **ChatGPT** and store them in a database for further reference. The application uses **Selenium** for scraping and saves the results in a structured format.

## Features 🌟
- ✅ **ChatGPT Conversation Scraping** – Automatically extract conversations from ChatGPT
- ✅ **Save Scraped Data** – Data is stored in the database using SQLAlchemy
- ✅ **User Authentication** – Users can log in and save their chat history
- ✅ **Export Data** – Export chat history in text format
- ✅ **Dark & Light Theme** – Switchable themes for better user experience

## Technologies Used 🔧
- **Python** (Main programming language)
- **Flask** (Web framework)
- **Flask-Login** (User authentication)
- **SQLAlchemy** (ORM for database management)
- **Selenium** (Browser automation for scraping)
- **PyMySQL** (Database connection for MySQL)

## Installation Guide 🚀

Follow these steps to install and run the application:

### 1. Install Dependencies
- Run the following script to install all required dependencies:
  ```
  install_requirements.bat
  ```

### 2. Setup the Database
- If the installation process is successful, run the following script:
  ```
  database_manager.bat
  ```
- Select the option **"Setup New Database"**

### 3. Run the Application
- After the database is successfully set up, start the application by executing:
  ```
  run_app.bat
  ```

### 4. Access the Application
- Once the application is running, click on the generated link to open it in your browser.

## Future Improvements 🚧
- 🔹 Support for more export formats
- 🔹 Enhanced security and authentication
- 🔹 More interactive UI

## Contributing 🤝
Feel free to fork this project and submit a pull request if you want to contribute!

## License 📜
This project is licensed under the MIT License.

---
For troubleshooting or additional configurations, refer to the documentation.

