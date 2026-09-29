# Snapdragon Setup Guide

> **⚠️ To verify on device**: The following instructions are for running on a Snapdragon X Windows ARM64 PC. They have not been fully verified on physical hardware yet.

## Prerequisites

### Hardware
- Snapdragon X Elite or Snapdragon X Plus powered HP PC
- Windows 11 on ARM64 (version 24H2 or later)
- Minimum 16GB RAM recommended
- NPU driver installed

### Software
- Qualcomm Neural Processing SDK for Windows
- ONNX Runtime with QNNExecutionProvider support
- Python 3.11+ (64-bit ARM)
- Visual Studio 2022 with ARM64 build tools (for building native extensions)

## Installation Steps

### 1. Install Qualcomm Neural Processing SDK

Download and install the Qualcomm Neural Processing SDK for Windows from the [Qualcomm Developer Network](https://developer.qualcomm.com/software/qualcomm-neural-processing-sdk).

```powershell
# Verify installation
qnn-version
```

### 2. Install ONNX Runtime with QNN Support

```powershell
# Option A: Install pre-built wheel (if available)
pip install onnxruntime-qnn

# Option B: Build from source (for latest features)
# See: https://onnxruntime.ai/docs/build/eps.html#qnn
```

### 3. Verify NPU Detection

```python
import onnxruntime as ort

providers = ort.get_available_providers()
print("Available providers:", providers)

# Should include QNNExecutionProvider
assert "QNNExecutionProvider" in providers
```

### 4. Configure Environment Variables

Create `.env` file in backend directory:

```env
USE_MOCK_ENGINES=false
PREFERRED_PROVIDERS=QNNExecutionProvider,CUDAExecutionProvider,DmlExecutionProvider,CPUExecutionProvider
VAD_MODEL_PATH=models/silero_vad.onnx
ASR_MODEL_PATH=models/whisper_tiny.onnx
```

### 5. Download ONNX Models

Models must be converted to ONNX format compatible with QNN:

```bash
# Download and convert Silero VAD
python scripts/download_models.py --model silero_vad

# Download and convert Whisper tiny
python scripts/download_models.py --model whisper_tiny
```

### 6. Model Conversion for QNN

Models need to be quantized and converted for QNN:

```python
# Example: Convert Whisper to QNN-compatible ONNX
# This requires Qualcomm AI Hub or local conversion tools
# See: https://github.com/quic/ai-hub-models
```

## Qualcomm AI Hub Integration

For optimal NPU performance, use Qualcomm AI Hub to compile models:

1. Create account at [Qualcomm AI Hub](https://aihub.qualcomm.com/)
2. Upload your ONNX model
3. Target: "Snapdragon X Elite" / "Windows on ARM"
4. Download compiled QNN context binary
5. Place in `models/` directory

## Running the Application

```bash
# Start backend
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd frontend
npm run dev
```

## Verification Checklist

- [ ] QNNExecutionProvider appears in `ort.get_available_providers()`
- [ ] `/api/v1/system/capabilities` shows `npu_available: true`
- [ ] VAD model loads with QNN provider
- [ ] ASR model loads with QNN provider
- [ ] Benchmark runs show NPU utilization
- [ ] Battery delta measurements work
- [ ] No fallback to CPU for VAD/ASR stages

## Troubleshooting

### QNNExecutionProvider not found
- Verify Qualcomm Neural Processing SDK is installed
- Check Windows version (requires 24H2+)
- Ensure ONNX Runtime was built/installed with QNN support
- Check PATH includes QNN libraries

### Model loading fails
- Verify model is valid ONNX format
- Check model input/output names match engine expectations
- Ensure model is quantized (INT8) for QNN
- Check model file path in `.env`

### Poor NPU performance
- Verify model is compiled for QNN (not just ONNX)
- Check thermal throttling
- Ensure power plan is "Best Performance"
- Close other NPU-intensive applications

### Battery measurements not working
- Requires Windows battery API access
- May not work in virtualized environments
- Check `psutil.sensors_battery()` availability

## Performance Targets (To Verify on Device)

| Stage | Target Latency (30s audio) | Target RTF |
|-------|---------------------------|------------|
| VAD   | < 50ms                    | < 0.001    |
| ASR   | < 500ms                   | < 0.02     |
| Summary | < 200ms                 | N/A        |

## Resources

- [ONNX Runtime QNN EP Documentation](https://onnxruntime.ai/docs/execution-providers/QNN-ExecutionProvider.html)
- [Qualcomm Neural Processing SDK](https://developer.qualcomm.com/software/qualcomm-neural-processing-sdk)
- [Qualcomm AI Hub](https://aihub.qualcomm.com/)
- [Silero VAD](https://github.com/snakers4/silero-vad)
- [Whisper ONNX](https://huggingface.co/onnx-community/whisper-tiny)