import { Box, Text, Stack, Title, Image, SimpleGrid } from '@mantine/core'
import ReactMarkdown from 'react-markdown'
import { useResearch, researchAssetUrl } from '@/api/hooks'

export interface ResearchPanelProps {
  slug: string
}

export function ResearchPanel({ slug }: ResearchPanelProps) {
  const { data, isLoading, isError } = useResearch(slug, true)

  if (isLoading) {
    return <Text c="dimmed" size="sm">Loading research…</Text>
  }

  if (isError) {
    return <Text c="red" size="sm">Failed to load research</Text>
  }

  const files = data?.files ?? []
  const images = data?.images ?? []

  if (files.length === 0 && images.length === 0) {
    return <Text c="dimmed" size="sm">No research collected yet.</Text>
  }

  return (
    <Stack gap="lg">
      {files.map((file) => (
        <Box key={file.name}>
          <Title order={5} mb="xs">{file.name}</Title>
          <ReactMarkdown>{file.content}</ReactMarkdown>
        </Box>
      ))}
      {images.length > 0 && (
        <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
          {images.map((name) => (
            <Image
              key={name}
              src={researchAssetUrl(slug, name)}
              alt={name}
              radius="sm"
            />
          ))}
        </SimpleGrid>
      )}
    </Stack>
  )
}
