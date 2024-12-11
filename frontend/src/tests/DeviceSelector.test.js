import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import DeviceSelector from "../components/DeviceSelector";

test("renders device selector", () => {
  const devices = [
    { _id: "1", external_id: "device1", dev_type: "Type 1" },
    { _id: "2", external_id: "device2", dev_type: "Type 2" }
  ];
  const onSelect = jest.fn();

  render(
    <DeviceSelector
      devices={devices}
      selectedDevice={null}
      onSelect={onSelect}
    />
  );

  // Проверка текста на экране
  expect(screen.getByText("Select a device:")).toBeInTheDocument();

  // Эмулируем изменение выбора в селекте
  fireEvent.change(screen.getByRole("combobox"), { target: { value: "device1" } });

  // Проверка, что onSelect был вызван с правильным значением
  expect(onSelect).toHaveBeenCalledWith("device1");
});
