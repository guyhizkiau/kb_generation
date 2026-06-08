import { AppShell } from '@mantine/core'
import { useDisclosure, useLocalStorage } from '@mantine/hooks'
import { NavSidebar } from './NavSidebar'
import { ArticlesView } from '@/views/articles/ArticlesView'
import { HealthView } from '@/views/health/HealthView'
import { FeedbackView } from '@/views/feedback/FeedbackView'
import { ArticleReaderOverlay } from '@/views/reader/ArticleReaderOverlay'
import { NavigationProvider, useNavigation } from '@/context/NavigationContext'

function ShellContent() {
  const { view: active, setView, readerSlug, closeReader } = useNavigation()
  const [collapsed, setCollapsed] = useLocalStorage({
    key: 'gw_sidebar_collapsed',
    defaultValue: false,
  })
  const [mobileOpened, { toggle: toggleMobile }] = useDisclosure()

  return (
    <>
      <AppShell
        header={{ height: 0 }}
        navbar={{
          width: collapsed ? 64 : 200,
          breakpoint: 'sm',
          collapsed: { mobile: !mobileOpened, desktop: false },
        }}
        padding="lg"
        transitionDuration={200}
        styles={{
          navbar: {
            backgroundColor: '#FFFFFF',
            borderRight: '1px solid rgba(0,0,0,0.06)',
          },
          main: {
            backgroundColor: '#F8F8FA',
          },
        }}
      >
        <AppShell.Navbar p={0}>
          <NavSidebar
            active={active}
            onSelect={(v) => {
              setView(v)
              if (mobileOpened) toggleMobile()
            }}
            collapsed={collapsed}
            onToggleCollapse={() => setCollapsed((v) => !v)}
            mobileOpened={mobileOpened}
            onMobileToggle={toggleMobile}
          />
        </AppShell.Navbar>

        <AppShell.Main>
          {active === 'articles' && <ArticlesView />}
          {active === 'health' && <HealthView />}
          {active === 'feedback' && <FeedbackView />}
        </AppShell.Main>
      </AppShell>

      {readerSlug && (
        <ArticleReaderOverlay slug={readerSlug} onClose={closeReader} />
      )}
    </>
  )
}

export function GhostwriterShell() {
  return (
    <NavigationProvider>
      <ShellContent />
    </NavigationProvider>
  )
}
