# Reverse Engineering Agents

This plugin provides specialized agents for reverse engineering and binary analysis tasks.

## Available Agents

### 🎯 IDA Pro Analyst
- Specializes in IDA Pro and Hex-Rays decompiler analysis
- Expert in cross-reference analysis and IDAPython scripting
- Ideal for deep binary analysis with IDA Pro

### 💻 Binary Expert
- Focuses on file format analysis (PE/ELF/Mach-O)
- Handles symbol recovery and structure reconstruction
- Perfect for static binary analysis tasks

### 🦠 Malware Analyst
- Malware family identification and behavior analysis
- IoC extraction and YARA rule creation
- MITRE ATT&CK framework mapping

### 🔓 Vulnerability Researcher
- Binary vulnerability discovery and fuzzing
- Exploit development concepts (educational)
- Mitigation bypass analysis

### 🛠️ Plugin Developer
- IDA Pro plugin development and customization
- Custom loader and processor modules
- IDAPython script optimization

### 🤖 Automation Expert
- Large-scale binary analysis pipelines
- CI/CD integration for security testing
- ML-powered analysis automation

## Usage

These agents are automatically loaded by Claude Code. You can invoke them by describing your needs, for example:

- "Help me analyze this binary with IDA Pro"
- "Is this sample malicious?"
- "Find vulnerabilities in this function"
- "Create an IDA plugin for my analysis"

## Installation

The agents are installed in:
```
C:\Users\ddo\AppData\Roaming\npm\.claude\plugins\reverse-engineering\
```

## Requirements

- Claude Code with agent support
- Optional: IDA Pro for advanced analysis
- Optional: Other analysis tools (Ghidra, Radare2, etc.)

## License

MIT License - See individual agent files for details