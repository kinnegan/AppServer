import React from "react";

const DeviceSelector = ({ devices, selectedDevice, onSelect }) => (
  <div className="device-selector">
    <label htmlFor="device-select">Select a device:</label>
    <select
      id="device-select"
      value={selectedDevice || ""}
      onChange={(e) => onSelect(e.target.value)}
    >
      <option value="" disabled>
        Choose a device
      </option>
      {devices.map((device) => (
        <option key={device._id} value={device.external_id}>
          {device.dev_type} - {device.external_id}
        </option>
      ))}
    </select>
  </div>
);

export default DeviceSelector;
