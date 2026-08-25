한국 퀴어 연극 아카이브 — 작품별 SNS 미리보기 설정

업로드 위치
1. index.html
   → GitHub 저장소 최상위(root)의 기존 index.html을 이 파일로 교체

2. scripts/generate_share_pages.py
   → 저장소에 scripts 폴더를 만들고 이 경로 그대로 업로드

3. .github/workflows/generate-share-pages.yml
   → .github/workflows 폴더를 만들고 이 경로 그대로 업로드

작동 방식
- 사이트의 SNS 공유 버튼은 이제
  https://queertheater.kr/share/작품ID/
  를 공유합니다.
- GitHub Actions가 WordPress REST API에서 공연을 읽어
  share/작품ID/index.html 페이지를 자동 생성합니다.
- 각 공유 페이지에는 작품 제목, 작품 설명/기본정보, 포스터 이미지가
  정적인 Open Graph / Twitter Card 메타데이터로 들어갑니다.
- 사람이 공유 링크를 클릭하면 자동으로
  https://queertheater.kr/#detail/작품ID
  로 이동합니다.

최초 1회
- 세 파일을 main 브랜치에 커밋합니다.
- GitHub → Actions → “Generate performance share pages”를 엽니다.
- Run workflow → main → Run workflow 를 한 번 눌러 즉시 생성합니다.
- 작업이 끝나면 저장소에 share/123/index.html 같은 폴더가 자동으로 생깁니다.
- 이 새 commit 뒤 GitHub Pages 배포가 끝나면 공유 미리보기가 사용할 수 있습니다.

이후
- WordPress에서 새 공연을 등록하거나 포스터를 바꾸면 30분 간격 스케줄이
  share 페이지를 자동 갱신합니다.
- 즉시 반영하고 싶으면 Actions에서 Run workflow를 수동 실행하면 됩니다.

주의
- X / Facebook / Bluesky 등이 예전에 읽은 URL의 미리보기를 캐시할 수 있습니다.
  새 /share/ID/ URL을 처음 공유하는 경우에는 작품 포스터가 바로 잡힐 가능성이 높습니다.
- 포스터가 없는 작품은 https://queertheater.kr/og-image.png 를 사용합니다.
