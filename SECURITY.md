# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | ✅                 |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly:

1. **Do not** create a public GitHub issue
2. Email us at **security@your-org.com** with details
3. Include steps to reproduce if possible
4. We will acknowledge receipt within 48 hours
5. We will provide a timeline for a fix within 7 days

## Security Considerations

### Data Privacy
- All audio processing happens locally on device
- No audio or transcripts are sent to external servers
- Database is stored locally (SQLite by default)
- No telemetry or analytics collected

### Authentication & Authorization
- Currently no authentication (single-user local app)
- Future versions may add user accounts
- API endpoints should be protected when exposed to network

### Dependencies
- Dependencies are pinned to specific versions
- Regular dependency updates via Dependabot
- Security advisories monitored via GitHub Dependabot alerts

### Network Security
- CORS configured to restrict origins
- WebSocket connections validated
- Input validation on all API endpoints
- Rate limiting recommended for production deployments

### NPU/GPU Access
- ONNX Runtime with QNNExecutionProvider requires:
  - Windows on ARM64
  - Qualcomm Neural Processing SDK
  - Proper driver installation
- No elevated privileges required for inference

## Secure Deployment Checklist

For production deployments:

- [ ] Use HTTPS (TLS 1.2+)
- [ ] Configure CORS for specific domains only
- [ ] Enable authentication if exposing to network
- [ ] Use PostgreSQL with SSL instead of SQLite
- [ ] Set secure headers (CSP, HSTS, etc.)
- [ ] Enable rate limiting
- [ ] Regular security scans
- [ ] Monitor for anomalous activity

## Vulnerability Disclosure Timeline

1. **Day 0**: Vulnerability reported
2. **Day 1-2**: Acknowledgment and initial assessment
3. **Day 3-7**: Root cause analysis and fix development
4. **Day 7-14**: Testing and verification
5. **Day 14+**: Release patch and public disclosure (if applicable)

We aim to release security patches within 14 days of verified reports.

## Contact

For security concerns, email: **security@your-org.com**

For general questions, open a [discussion](https://github.com/your-org/Hexacode/discussions).