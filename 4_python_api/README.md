# Readme for the data handler.

- This code enables you to record ADC values from the EEG hardware within a specific time range.
- The date is stored in binary and can be accessed via binary_ready.py.


The recording took place within the `DataHandler` module. You can specify the duration and provide information about the recording for the metadata.

The `BinaryReady` module can be used to open stored measurement values. To do this, the path to the measurement values and the corresponding path to the timestamp must be specified.