#include <Python.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// Function to detect ultrasonic signatures in signal data
static PyObject* detect_ultrasonic_signature(PyObject* self, PyObject* args) {
    PyObject* signal_list;
    double threshold;
    
    // Parse arguments
    if (!PyArg_ParseTuple(args, "Od", &signal_list, &threshold)) {
        return NULL;
    }
    
    // Convert Python list to C array
    if (!PyList_Check(signal_list)) {
        PyErr_SetString(PyExc_TypeError, "First argument must be a list");
        return NULL;
    }
    
    Py_ssize_t length = PyList_Size(signal_list);
    double* signal = malloc(length * sizeof(double));
    
    for (Py_ssize_t i = 0; i < length; i++) {
        PyObject* item = PyList_GetItem(signal_list, i);
        if (!PyFloat_Check(item)) {
            free(signal);
            PyErr_SetString(PyExc_TypeError, "List items must be floats");
            return NULL;
        }
        signal[i] = PyFloat_AsDouble(item);
    }
    
    // Perform detection
    int ultrasonic_count = 0;
    double average_power = 0.0;
    
    // Calculate average power
    for (Py_ssize_t i = 0; i < length; i++) {
        average_power += signal[i] * signal[i];
    }
    average_power /= length;
    
    // Detect peaks above threshold
    for (Py_ssize_t i = 1; i < length - 1; i++) {
        if (signal[i] > threshold && 
            signal[i] > signal[i-1] && 
            signal[i] > signal[i+1]) {
            ultrasonic_count++;
        }
    }
    
    // Clean up
    free(signal);
    
    // Return result
    int detected = (average_power > threshold * threshold && ultrasonic_count > 5) ? 1 : 0;
    return PyBool_FromLong(detected);
}

// Function to apply resonant frequency overload
static PyObject* apply_resonant_overload(PyObject* self, PyObject* args) {
    PyObject* signal_list;
    double frequency;
    double intensity;
    
    // Parse arguments
    if (!PyArg_ParseTuple(args, "Odd", &signal_list, &frequency, &intensity)) {
        return NULL;
    }
    
    // Convert Python list to C array
    if (!PyList_Check(signal_list)) {
        PyErr_SetString(PyExc_TypeError, "First argument must be a list");
        return NULL;
    }
    
    Py_ssize_t length = PyList_Size(signal_list);
    double* signal = malloc(length * sizeof(double));
    
    for (Py_ssize_t i = 0; i < length; i++) {
        PyObject* item = PyList_GetItem(signal_list, i);
        if (!PyFloat_Check(item)) {
            free(signal);
            PyErr_SetString(PyExc_TypeError, "List items must be floats");
            return NULL;
        }
        signal[i] = PyFloat_AsDouble(item);
    }
    
    // Apply resonant frequency overload
    for (Py_ssize_t i = 0; i < length; i++) {
        // Add resonant frequency component
        double resonant_component = intensity * sin(2 * M_PI * frequency * i / length);
        signal[i] += resonant_component;
        
        // Apply non-linear distortion to simulate overload
        if (signal[i] > 0.9) {
            signal[i] = 0.9 + 0.1 * tanh(signal[i] - 0.9);
        } else if (signal[i] < -0.9) {
            signal[i] = -0.9 + 0.1 * tanh(signal[i] + 0.9);
        }
    }
    
    // Convert back to Python list
    PyObject* result_list = PyList_New(length);
    for (Py_ssize_t i = 0; i < length; i++) {
        PyList_SetItem(result_list, i, PyFloat_FromDouble(signal[i]));
    }
    
    // Clean up
    free(signal);
    
    return result_list;
}

// Method definitions
static PyMethodDef SignalProcessingMethods[] = {
    {"detect_ultrasonic_signature", detect_ultrasonic_signature, METH_VARARGS, "Detect ultrasonic signatures in signal data"},
    {"apply_resonant_overload", apply_resonant_overload, METH_VARARGS, "Apply resonant frequency overload to a signal"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef signalprocessingmodule = {
    PyModuleDef_HEAD_INIT,
    "signal_processing_ext",
    "Signal processing functions for threat elimination",
    -1,
    SignalProcessingMethods
};

// Module initialization
PyMODINIT_FUNC PyInit_signal_processing_ext(void) {
    return PyModule_Create(&signalprocessingmodule);
}