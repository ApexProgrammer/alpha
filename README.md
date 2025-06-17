# Alpha - Honeypot Threat Intelligence Solution

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)

A machine learning-powered honeypot that detects and tracks malicious login attempts with real-time geolocation mapping and threat analysis.

## Screenshots

![SecureBank Login Page](README-images/fake-login.png)
![SecureBank Admin Panel](README-images/fake-admin-panel.png)
![Analytics Dashboard](README-images/dashboard.png)

## Features

- AI-powered threat detection using K-means clustering
- Real-time geolocation mapping of attack origins
- Adaptive learning with automatic model retraining
- Deceptive admin panel to trap attackers
- Live analytics dashboard with threat visualization
- Comprehensive attack logging and analysis

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/ApexProgrammer/alpha.git
   cd alpha
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run setup and start:
   ```bash
   python setup.py
   python app.py
   ```

## Access Points

- Honeypot Login: `http://localhost:5000`
- Analytics Dashboard: `http://localhost:5000/dashboard`
- Admin Panel: `http://localhost:5000/admin`

## Configuration

Copy `.env.example` to `.env` and customize as needed. Key settings:

- `SECRET_KEY`: Flask secret key
- `HOST`: Server bind address
- `DEBUG`: Debug mode (disable in production)
- `RETRAIN_THRESHOLD`: ML model retraining frequency

## How It Works

The system uses K-means clustering to analyze login attempts based on username patterns, password complexity, and IP characteristics. Normal users see login failures while detected attackers are redirected to a fake admin panel for behavioral analysis. All attempts are logged with geolocation data for threat intelligence.

## Tech Stack

- Backend: Python Flask
- Machine Learning: Scikit-learn
- Frontend: HTML5, CSS3, JavaScript
- Mapping: Leaflet.js with OpenStreetMap
- Storage: CSV logging with JSON caching
## Project Structure

```
alpha/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── setup.py               # Setup script
├── requirements.txt       # Dependencies
├── retrain_model.py       # ML model retraining
├── templates/             # HTML templates
├── tests/                 # Test suite
└── README-images/         # Documentation images
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/name`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/name`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Legal Disclaimer

For educational and research purposes only. Users are responsible for compliance with applicable laws and regulations.

---

**Alpha - Honeypot Threat Intelligence Solution**  
*Created by Ryan Casey*  
*Contact: ryancasey.dev@gmail.com*
