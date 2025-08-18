#!/bin/bash

echo "🔍 Python Environment Diagnostic"
echo "================================"

echo ""
echo "📋 Environment Variables:"
echo "CONDA_DEFAULT_ENV: ${CONDA_DEFAULT_ENV:-'Not set'}"
echo "CONDA_PREFIX: ${CONDA_PREFIX:-'Not set'}"
echo "VIRTUAL_ENV: ${VIRTUAL_ENV:-'Not set'}"
echo "PATH: $PATH"

echo ""
echo "🐍 Python Executables:"
echo "which python3: $(which python3 2>/dev/null || echo 'Not found')"
echo "which python: $(which python 2>/dev/null || echo 'Not found')"

echo ""
echo "📊 Python Versions:"
echo "python3 --version: $(python3 --version 2>/dev/null || echo 'Not found')"
echo "python --version: $(python --version 2>/dev/null || echo 'Not found')"

echo ""
echo "🅰️ Anaconda/Conda Info:"
if command -v conda &> /dev/null; then
    echo "Conda version: $(conda --version)"
    echo "Active environment: $(conda info --envs | grep '*' || echo 'None active')"
    echo "Available environments:"
    conda env list
else
    echo "Conda not found in PATH"
fi

echo ""
echo "💡 Recommendations:"
if [[ "$CONDA_DEFAULT_ENV" != "" ]]; then
    echo "✅ You're in conda environment: $CONDA_DEFAULT_ENV"
    python_version=$(python --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+' | head -1)
    if [[ ! -z "$python_version" ]]; then
        python_major=$(echo $python_version | cut -d. -f1)
        python_minor=$(echo $python_version | cut -d. -f2)
        if [[ $python_major -eq 3 && $python_minor -ge 11 ]]; then
            echo "✅ Python version $python_version is compatible"
            echo "🎯 You can run: ./setup.sh"
        else
            echo "❌ Python version $python_version is too old"
            echo "🎯 Try: conda install python=3.12"
        fi
    fi
else
    echo "⚠️  No conda environment active"
    echo "🎯 Try one of these:"
    echo "   - conda activate your-environment-name"
    echo "   - ./setup-conda.sh (creates new environment)"
fi 