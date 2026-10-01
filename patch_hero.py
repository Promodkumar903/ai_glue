import os, shutil, re

BASE = r'C:\Users\Administrator\ai_glue\frontend\src'

# ===== 1. Backup Components.jsx =====
comp_path = os.path.join(BASE, 'components', 'ui', 'Components.jsx')
shutil.copy(comp_path, comp_path + '.bak_pre_hero')
print('Backup: Components.jsx.bak_pre_hero')

with open(comp_path, 'r', encoding='utf-8') as f:
    comp = f.read()

OLD_PH = '''export const PageHeader = ({ title, subtitle, action, icon }) => (
    <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 mb-6 pb-4 border-b border-gray-200">
      <div>
        <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">{icon && <span>{icon}</span>}{title}</h1>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {action && <div className="flex gap-2 flex-wrap">{action}</div>}
    </div>
  );'''

NEW_PH = '''export const PageHeader = ({ title, subtitle, action, icon, image }) => {
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

if OLD_PH in comp:
    comp = comp.replace(OLD_PH, NEW_PH)
    with open(comp_path, 'w', encoding='utf-8') as f:
        f.write(comp)
    print('Updated PageHeader with hero support')
else:
    print('WARNING: PageHeader pattern not found - skipping')

# ===== 2. Patch all pages with image prop =====
# Unsplash URLs per page/route
IMAGES = {
    # Student pages
    'pages/student/Education.jsx': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80',
    'pages/student/StudentLife.jsx': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=1600&q=80',
    'pages/student/Journey.jsx': 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1600&q=80',
    'pages/student/Scholarships.jsx': 'https://images.unsplash.com/photo-1564981797816-1043664bf78d?w=1600&q=80',
    'pages/student/Books.jsx': 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=1600&q=80',
    'pages/student/Visa.jsx': 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1600&q=80',
    'pages/student/Documents.jsx': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80',
    'pages/student/Jobs.jsx': 'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=1600&q=80',
    'pages/student/Housing.jsx': None,  # already has Hero
    # Student-new
    'pages/student-new/ApplyCollege.jsx': 'https://images.unsplash.com/photo-1607237138185-eedd9c632b0b?w=1600&q=80',
    'pages/student-new/BooksLibrary.jsx': 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1600&q=80',
    'pages/student-new/DocumentsVault.jsx': 'https://images.unsplash.com/photo-1568667256549-094345857637?w=1600&q=80',
    'pages/student-new/MyApplications.jsx': 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1600&q=80',
    'pages/student-new/SeatAvailability.jsx': 'https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=1600&q=80',
    # Job seeker
    'pages/jobseeker-new/JobSearch.jsx': 'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1600&q=80',
    'pages/jobseeker-new/UploadResume.jsx': 'https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=1600&q=80',
    'pages/jobseeker-new/MyApplications.jsx': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&q=80',
    'pages/jobseeker-new/DocumentsVault.jsx': 'https://images.unsplash.com/photo-1568667256549-094345857637?w=1600&q=80',
    'pages/jobseeker-new/Offers.jsx': 'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=1600&q=80',
    'pages/jobseeker-new/VisaTracker.jsx': 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1600&q=80',
    'pages/jobseeker-new/Accommodation.jsx': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1600&q=80',
    'pages/job-seeker/Vacancies.jsx': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1600&q=80',
    'pages/job-seeker/Applications.jsx': 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1600&q=80',
    'pages/job-seeker/Interviews.jsx': 'https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=1600&q=80',
    'pages/job-seeker/Offers.jsx': 'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=1600&q=80',
    'pages/job-seeker/Deals.jsx': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&q=80',
    'pages/job-seeker/Accommodation.jsx': 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=1600&q=80',
    # Agent
    'pages/agent-new/Candidates.jsx': 'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=1600&q=80',
    'pages/agent-new/Funnel.jsx': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1600&q=80',
    'pages/agent-new/Commission.jsx': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80',
    'pages/agent-new/ReferralLink.jsx': 'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=1600&q=80',
    # Broker
    'pages/broker-new/AgentLeaderboard.jsx': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1600&q=80',
    'pages/broker-new/CommissionTracker.jsx': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80',
    'pages/broker-new/ClientDistribution.jsx': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1600&q=80',
    # Employer
    'pages/employer-new/PostJob.jsx': 'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=1600&q=80',
    'pages/employer-new/ApplicantTracking.jsx': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&q=80',
    'pages/employer-new/Contracts.jsx': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600&q=80',
    # Admin
    'pages/admin-new/EducationControl.jsx': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80',
    'pages/admin-new/VendorControl.jsx': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1600&q=80',
    'pages/admin-new/JobSeekerCommand.jsx': 'https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=1600&q=80',
    'pages/admin-new/StudentCommand.jsx': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80',
    'pages/admin-new/AgentBrokerCommand.jsx': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1600&q=80',
    'pages/admin-new/RevenueAnalytics.jsx': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1600&q=80',
    'pages/admin-new/BulkOperations.jsx': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1600&q=80',
    # Study/Work/Trust
    'pages/study-abroad/StudyAbroad.jsx': 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=1600&q=80',
    'pages/work-abroad/WorkAbroad.jsx': 'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1600&q=80',
    'pages/trust/TrustDirectory.jsx': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1600&q=80',
}

patched = 0
for rel, img in IMAGES.items():
    if img is None:
        continue
    full = os.path.join(BASE, rel.replace('/', os.sep))
    if not os.path.exists(full):
        continue
    with open(full, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'image=' in content:
        # already has image prop
        continue

    # Find <PageHeader ... /> and add image prop
    # Handle multi-line PageHeader
    def add_image(match):
        block = match.group(0)
        if block.rstrip().endswith('/>'):
            # single or multi-line self-closing
            inner = block.rstrip()[:-2].rstrip()
            return inner + '\n        image="' + img + '"\n      />'
        return block

    pattern = re.compile(r'<PageHeader\b[^>]*?/>', re.DOTALL)
    new_content = pattern.sub(add_image, content)

    if new_content != content:
        shutil.copy(full, full + '.bak_hero')
        with open(full, 'w', encoding='utf-8') as f:
            f.write(new_content)
        patched += 1
        print('Patched: ' + rel)

print('Total patched: %d' % patched)
print('DONE')