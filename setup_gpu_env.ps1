param(
    [string]$EnvName = "cvdemo"
)

$ErrorActionPreference = "Stop"

Write-Host "Creating conda environment: $EnvName"
conda create -n $EnvName python=3.11 -y

Write-Host "Installing CUDA-enabled PyTorch"
conda run -n $EnvName pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

Write-Host "Installing project requirements"
conda run -n $EnvName pip install -r requirements.txt

Write-Host "Verifying CUDA access"
conda run -n $EnvName python -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no gpu')"

Write-Host "Done. Activate with: conda activate $EnvName"
