#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <unistd.h>  // for chdir, getcwd
#include <stdio.h>
#include <stdlib.h>

// Declare your main function (from nbody_comp.c)
extern int main(int argc, char* argv[]);

static PyObject* run_nbody_simulation(PyObject* self, PyObject* args) {
    char *input_file_path;
    char *output_dir_path;
    
    // Parse arguments from Python: input file path and output directory
    if (!PyArg_ParseTuple(args, "ss", &input_file_path, &output_dir_path)) {
        return NULL;
    }
    
    printf("N-body simulation starting...\n");
    printf("Input file: %s\n", input_file_path);
    printf("Output directory: %s\n", output_dir_path);
    
    // Save current working directory
    char original_dir[1024];
    if (getcwd(original_dir, sizeof(original_dir)) == NULL) {
        PyErr_SetString(PyExc_OSError, "Cannot get current directory");
        return NULL;
    }
    
    // Change to output directory (where your C code will write files)
    if (chdir(output_dir_path) != 0) {
        PyErr_SetString(PyExc_OSError, "Cannot change to output directory");
        return NULL;
    }
    
    // Set up arguments for your main function
    char *argv_sim[] = {"nbody_comp", input_file_path, NULL};
    int argc_sim = 2;
    
    // Call your modified main function
    int result = main(argc_sim, argv_sim);
    
    // Restore original directory
    if (chdir(original_dir) != 0) {
        printf("Warning: Could not restore original directory\n");
    }
    
    printf("N-body simulation completed with return code: %d\n", result);
    
    // Return result to Python (0 = success, non-zero = error)
    return PyLong_FromLong(result);
}

// Method definitions for the Python module
static PyMethodDef nbody_methods[] = {
    {"run_nbody_simulation", run_nbody_simulation, METH_VARARGS,
     "Run N-body simulation with input file and output directory"},
    {NULL, NULL, 0, NULL}  // Sentinel (end marker)
};

// Module definition
static struct PyModuleDef nbody_module = {
    PyModuleDef_HEAD_INIT,
    "_nbody_c",                          // Module name
    "N-body simulation C extension",     // Module description
    -1,                                  // Size of per-interpreter state
    nbody_methods                        // Method definitions
};

// Module initialization function (called when Python imports the module)
PyMODINIT_FUNC PyInit__nbody_c(void) {
    return PyModule_Create(&nbody_module);
}
