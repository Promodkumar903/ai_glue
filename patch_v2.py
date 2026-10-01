import os, shutil, re

BASE = r'C:\Users\Administrator\ai_glue\frontend\src'
APP = os.path.join(BASE, 'App.jsx')
COMP = os.path.join(BASE, 'components', 'ui', 'Components.jsx')

# ===== Backup =====
shutil.copy(APP, APP + '.bak_v2')
shutil.copy(COMP, COMP + '.bak_v2')
print('Backups: App.jsx.bak_v2, Components.jsx.bak_v2')

# ===== FIX 1: PageHeader with image support =====
with open(COMP, 'r', encoding='utf-8') as f:
    comp = f.read()

# Find PageHeader function using markers
start_idx = comp.find('export const PageHeader = ')
if start_idx != -1:
    end_marker = '\n  );'
    end_idx = comp.find(end_marker, start_idx)
    if end_idx != -1:
        end_idx += len(end_marker)
        old_header = comp[start_idx:end_idx]
        print('Found PageHeader block, length: %d' % len(old_header))

        new_header = '''export const PageHeader = ({ title, subtitle, action, icon, image }) => {
    if (image) {
      return (
        <div className="relative rounded-2xl overflow-hidden mb-6 shadow-xl">
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: `url('${image}')` }}
          />
          <div className="absolute inset-0 bg-gradient-to-r from-slate-900/90 via-slate-900/70 to-transparent" />
          <div className="relative p-8 md:p-10 flex flex-col sm:flex-row sm:justify-between sm:items-end gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white flex items-center gap-2">
                {icon && <span>{icon}</span>}{title}
              </h1>
              {subtitle && <p className="text-slate-200 mt-2 text-sm md:text-base">{subtitle}</p>}
            </div>
            {action && <div className="flex gap-2 flex-wrap">{action}</div>}
          </div>
        </div>
      );
    }
    return (
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-6 pb-4 border-b border-gray-200">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">{icon && <span>{icon}</span>}{title}</h1>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
        {action && <div className="flex gap-2 flex-wrap">{action}</div>}
      </div>
    );
  };'''

        comp = comp[:start_idx] + new_header + comp[end_idx:]
        with open(COMP, 'w', encoding='utf-8') as f:
            f.write(comp)
        print('PageHeader UPDATED with image support')
    else:
        print('ERROR: Could not find closing of PageHeader')
else:
    print('ERROR: PageHeader not found')

# ===== FIX 2: Move routes inside Layout =====
with open(APP, 'r', encoding='utf-8') as f:
    app = f.read()

# Find block to move
start_marker = '      <Route path="/admin/agents-brokers"'
end_marker = '      <Route path="/jobseeker-new/documents" element={<DocumentsVault />} />'

s_idx = app.find(start_marker)
e_idx = app.find(end_marker)

if s_idx != -1 and e_idx != -1:
    e_idx += len(end_marker)
    block = app[s_idx:e_idx]
    print('Found block to move: %d chars' % len(block))

    # Remove from original
    app = app[:s_idx] + app[e_idx:]

    # Find Layout closing (before {/* Default */})
    default_marker = '      {/* Default */}'
    d_idx = app.find(default_marker)

    if d_idx != -1:
        # Find the </Route> immediately before
        close_idx = app.rfind('      </Route>', 0, d_idx)
        if close_idx != -1:
            # Re-indent block (add 2 spaces to each non-empty line)
            indented = '\n'.join(
                ('  ' + line if line.strip() else line)
                for line in block.split('\n')
            )
            app = app[:close_idx] + indented + '\n\n' + app[close_idx:]
            print('Routes MOVED inside Layout')
        else:
            print('ERROR: Layout closing not found')
    else:
        print('ERROR: Default marker not found')

    with open(APP, 'w', encoding='utf-8') as f:
        f.write(app)
    print('App.jsx SAVED')
else:
    print('ERROR: Route block not found')

print('DONE')