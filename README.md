# NirmalNOOBBOT - Empathetic AI Companion

An intelligent robotics system that recognizes and responds to human emotions with empathy. This project integrates **Artificial Intelligence**, **Computer Vision**, and **Natural Language Processing** to create meaningful human-machine interactions through emotional awareness.

## 🤖 Project Overview

**NirmalNOOBBOT** is an emotionally intelligent AI companion that:
- 🎭 Detects human emotions through facial analysis and speech recognition
- 💬 Responds empathetically using conversational AI (Groq LLM)
- 🔊 Speaks back with natural text-to-speech synthesis
- 🎯 Learns and adapts to improve responses over time
- 📱 Runs on Windows, Linux, and Raspberry Pi 5

### Potential Applications
- Mental health monitoring and support
- Elderly care companionship
- Educational assistance
- General emotional well-being support

## 🛠️ Hardware Components

- **Raspberry Pi 5** (4GB RAM) - Main processor
- **Raspberry Pi Camera Module** (or USB webcam)
- **USB Microphone** or USB speaker+mic combo
- **ESP32** - IoT microcontroller
- **L298N Motor Driver** - Motor control
- **Ultrasonic Sensors** - Distance detection
- **Motors & Batteries** (2.5V x 4) - Movement

## 📋 Features

- **Multi-modal Emotion Recognition**: Combines facial expression detection, speech emotion analysis, and NLP
- **Deep Learning**: Uses CNNs for visual processing and RNNs for audio analysis
- **Reinforcement Learning**: Continuously improves responses through user interaction
- **Offline TTS**: Text-to-speech synthesis without cloud dependency
- **API-based Conversation**: Integrates with Groq API for fast, empathetic responses
- **Cross-platform**: Runs on Windows, Linux, and Raspberry Pi

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Webcam & Microphone
- Internet connection (for initial setup & API calls)

### Installation

#### Windows
```powershell
# Clone the repository
git clone https://github.com/vivvek69/AI-Comapnion.git
cd NirmalNOOBBOT

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

#### Linux / Raspberry Pi
```bash
# Install system dependencies
sudo apt update
sudo apt install espeak-ng libespeak1 libatlas-base-dev libhdf5-dev libgtk-3-dev python3-pip

# Clone and setup
git clone https://github.com/vivvek69/AI-Comapnion.git
cd NirmalNOOBBOT
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python3 main.py
```

### Configuration

1. Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

2. Get your API key from [Groq Console](https://console.groq.com)

### Usage

```bash
python main.py
```

- **View camera feed** with emotion overlays
- **Speak to the AI** - it will listen and respond
- Press **q** to quit the application

## 📁 Project Structure

```
NirmalNOOBBOT/
├── main.py                    # Main application entry point
├── ai_companion.py            # Core AI companion logic
├── emotion_detector.py        # Facial emotion detection
├── voice_io.py               # Speech recognition & synthesis
├── feedback_learning.py       # Reinforcement learning module
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── requirements-pi.txt       # Raspberry Pi specific deps
├── Dockerfile               # Docker containerization
├── docker-compose.yml       # Docker compose setup
├── CONNECTION.md            # Deployment & connection guide
├── Details.md               # Project details
├── PROJECT_CHANGES.md       # Change log
└── scripts/
    └── run-native.sh        # Native run script
```

## 🔧 Key Technologies

| Component | Technology |
|-----------|-----------|
| **Emotion Detection** | FER (Facial Emotion Recognition), Keras CNN |
| **Computer Vision** | OpenCV |
| **Speech Recognition** | Google Speech Recognition API |
| **Text-to-Speech** | pyttsx3 (offline) |
| **Conversational AI** | Groq API (LLM) |
| **Control Flow** | Python 3.11+ |
| **Deployment** | Docker, Raspberry Pi OS |

## 📦 Dependencies

See `requirements.txt` for complete list. Key packages:
- **opencv-python** - Video capture & face detection
- **fer** - Facial emotion recognition
- **SpeechRecognition** - Audio to text
- **pyttsx3** - Text to speech
- **groq** - AI conversation API
- **python-dotenv** - Environment configuration

## 🐳 Docker Deployment

```bash
# Build and run with Docker
docker-compose up --build

# Or use the provided scripts
./run-docker.sh        # Linux/Mac
.\run-docker.bat       # Windows
```

## 📡 Raspberry Pi Deployment

See [CONNECTION.md](CONNECTION.md) for detailed Raspberry Pi setup instructions, including:
- SCP file transfer
- Camera module configuration
- Audio setup
- ESP32 motor control wiring

## 🧠 How It Works

1. **Capture**: Webcam/Camera captures user's face and microphone records audio
2. **Detect**: Emotion detector analyzes facial expressions and speech patterns
3. **Understand**: NLP processes the user's spoken input
4. **Respond**: Groq LLM generates empathetic responses
5. **Deliver**: Text-to-speech speaks the response while updating motor controls
6. **Learn**: Feedback system tracks interaction quality and improves future responses

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source. Feel free to use, modify, and distribute.

## 🆘 Troubleshooting

### ImportError on VS Code
- Run: `Ctrl+Shift+P` → `Python: Select Interpreter`
- Select the `.venv` interpreter

### Camera/Microphone Not Working
- Check device permissions
- Ensure camera/mic are not in use by another application
- Restart the application

### Groq API Errors
- Verify `.env` file has correct `GROQ_API_KEY`
- Check internet connection
- Visit [Groq Console](https://console.groq.com) to verify key validity

### Raspberry Pi Issues
- See [CONNECTION.md](CONNECTION.md) for detailed troubleshooting

## 📚 References

- [Groq API Documentation](https://docs.groq.com)
- [OpenCV Tutorials](https://docs.opencv.org/master/d9/df8/tutorial_root.html)
- [Raspberry Pi Documentation](https://www.raspberrypi.com/documentation/)
- [FER (Facial Emotion Recognition)](https://github.com/justinshenk/fer)

## 👨‍💻 Author

**NirmalNOOBBOT Development Team**

## 🌟 Acknowledgments

Built with ❤️ to promote empathetic human-AI interaction and emotional well-being.

---

**Last Updated**: April 2026  
**Status**: Active Development  
**Python Version**: 3.11+
