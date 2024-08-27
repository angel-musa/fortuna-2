@echo off

:: Navigate to the directory containing your Python script
cd C:\projects\fortunafinal\Scripts

:: Run your Python script
python image_fetcher.py

:: Add the generated file(s) to git
git add company_images

:: Commit the changes with a message
git commit -m "Automated update of sentiment plots"

:: Push the changes to your GitHub repository
git push origin main
