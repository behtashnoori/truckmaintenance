$patterns = @("DataBase", "*.mdf", "*.ldf", "*.sqlite*", "*.bak", "*.log")
foreach ($p in $patterns) {
  git rm -r --cached --ignore-unmatch $p
}
git add .gitattributes .gitignore
Write-Host "Cleaned tracked DB/log files from index. Now commit these changes."
