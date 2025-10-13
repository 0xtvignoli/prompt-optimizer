#!/bin/bash
# Script helper per configurare GitHub remote e fare push

echo "==================================="
echo "Setup GitHub per Prompt Optimizer"
echo "==================================="
echo ""

# Check if gh CLI is available
if command -v gh &> /dev/null; then
    echo "✓ GitHub CLI (gh) trovato!"
    echo ""
    echo "Vuoi creare un nuovo repository su GitHub? (y/n)"
    read -r response
    
    if [[ "$response" == "y" ]]; then
        echo ""
        echo "Creazione repository 'prompt-optimizer'..."
        gh repo create prompt-optimizer \
            --public \
            --source=. \
            --description="Python package for optimizing LLM prompts - reduces costs by 20-35%" \
            --push
        
        echo ""
        echo "✅ Repository creato e push completato!"
        echo "🌐 Visualizza su: https://github.com/$(gh api user -q .login)/prompt-optimizer"
    fi
else
    echo "⚠ GitHub CLI (gh) non trovato."
    echo ""
    echo "Opzioni:"
    echo "1. Installa gh CLI: https://cli.github.com/"
    echo "2. Crea repository manualmente su github.com"
    echo ""
    echo "Dopo aver creato il repository, esegui:"
    echo ""
    echo "  git remote add origin https://github.com/USERNAME/prompt-optimizer.git"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    echo ""
fi

echo ""
echo "==================================="
echo "Repository info:"
echo "==================================="
git remote -v
echo ""
echo "Branch:"
git branch
echo ""
echo "Last commit:"
git log -1 --oneline
echo ""
