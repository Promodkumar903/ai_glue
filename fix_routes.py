import os, shutil

APP = r'C:\Users\Administrator\ai_glue\frontend\src\App.jsx'
shutil.copy(APP, APP + '.bak_routes')
print('Backup: App.jsx.bak_routes')

with open(APP, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Route block to move (find by unique markers)
start_needle = '<Route path="/admin/agents-brokers"'
end_needle = '<Route path="/jobseeker-new/documents"'

s_idx = None
e_idx = None
for i, line in enumerate(lines):
    if start_needle in line and s_idx is None:
        s_idx = i
    if end_needle in line and s_idx is not None:
        e_idx = i
        break

if s_idx is None or e_idx is None:
    print('ERROR: markers not found. s=%s e=%s' % (s_idx, e_idx))
    exit(1)

print('Block found: lines %d to %d' % (s_idx + 1, e_idx + 1))

# Extract block
block = lines[s_idx:e_idx+1]

# Remove from original (also remove one preceding blank line if present)
del lines[s_idx:e_idx+1]
if s_idx > 0 and lines[s_idx-1].strip() == '':
    del lines[s_idx-1]

# Find insert point - after the /trust route (inside Layout)
insert_needle = '<Route path="/trust"'
insert_idx = None
for i, line in enumerate(lines):
    if insert_needle in line:
        insert_idx = i
        break

if insert_idx is None:
    print('ERROR: insert point not found')
    exit(1)

print('Insert at line: %d' % (insert_idx + 1))

# Add +2 spaces indentation (from 6 to 8)
indented = []
for l in block:
    if l.strip():
        indented.append('  ' + l)
    else:
        indented.append(l)

# Insert after the /trust line
lines = lines[:insert_idx+1] + indented + ['\n'] + lines[insert_idx+1:]

with open(APP, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('DONE - Routes moved inside Layout')
print('Total lines now: %d' % len(lines))