# Embedded Systems and IoT

This is an optional specialist development team from the source workflow.

Primary A-level artifact: an embedded delivery pack covering hardware interfaces, firmware, real-time and resource constraints, connectivity, reliability, hardware-in-the-loop tests, and security.

## Topology

- A: [Embedded Systems Manager](./embedded-systems-manager.toml) - `embedded-systems-manager`
  - B: [Hardware Integration Lead](./embedded-systems-hardware-integration-lead.toml) - `embedded-systems-hardware-integration-lead`
    - C: [Sensor Specialist](./embedded-systems-sensor-specialist.toml) - `embedded-systems-sensor-specialist`
    - C: [Driver Developer](./embedded-systems-driver-developer.toml) - `embedded-systems-driver-developer`
    - C: [Hardware Interface Specialist](./embedded-systems-hardware-interface-specialist.toml) - `embedded-systems-hardware-interface-specialist`
  - B: [Firmware Lead](./embedded-systems-firmware-lead.toml) - `embedded-systems-firmware-lead`
    - C: [Real-Time Systems Developer](./embedded-systems-real-time-systems-developer.toml) - `embedded-systems-real-time-systems-developer`
    - C: [Memory-Constrained Developer](./embedded-systems-memory-constrained-developer.toml) - `embedded-systems-memory-constrained-developer`
    - C: [Power Management Specialist](./embedded-systems-power-management-specialist.toml) - `embedded-systems-power-management-specialist`
  - B: [Connectivity Lead](./embedded-systems-connectivity-lead.toml) - `embedded-systems-connectivity-lead`
    - C: [Bluetooth Specialist](./embedded-systems-bluetooth-specialist.toml) - `embedded-systems-bluetooth-specialist`
    - C: [Wi-Fi Specialist](./embedded-systems-wi-fi-specialist.toml) - `embedded-systems-wi-fi-specialist`
    - C: [Device Protocol Specialist](./embedded-systems-device-protocol-specialist.toml) - `embedded-systems-device-protocol-specialist`
  - B: [Device Quality Lead](./embedded-systems-device-quality-lead.toml) - `embedded-systems-device-quality-lead`
    - C: [Hardware-in-the-Loop Tester](./embedded-systems-hardware-in-the-loop-tester.toml) - `embedded-systems-hardware-in-the-loop-tester`
    - C: [Reliability Tester](./embedded-systems-reliability-tester.toml) - `embedded-systems-reliability-tester`
    - C: [Firmware Security Reviewer](./embedded-systems-firmware-security-reviewer.toml) - `embedded-systems-firmware-security-reviewer`

## Operating boundary

The A manager and B leads are read-only synthesis roles. C specialists that are inherently analytical or review-oriented are also explicitly read-only. Implementation-capable C specialists inherit the parent session sandbox, but their prompts require explicit edit authority and exclusive file ownership before changes.

These files are drafts and are not auto-discovered from this folder. Copy only the roles needed for a workflow into a supported Codex agent directory.
