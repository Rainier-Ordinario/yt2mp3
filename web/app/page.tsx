import { InfiniteGrid } from "@/components/ui/infinite-grid";
import { YouTubeConverter } from "@/components/youtube-converter";

export default function Home() {
  return (
    <InfiniteGrid>
      <YouTubeConverter />
    </InfiniteGrid>
  );
}
