import click
from colorama import init, Fore, Back, Style
from parsers import parse_video
from downloader import VideoDownloader
from utils import extract_urls, is_valid_url

init(autoreset=True)

@click.group()
def cli():
    pass

@cli.command('download')
@click.argument('url')
@click.option('--output', '-o', help='Output directory')
def download_command(url, output):
    if not is_valid_url(url):
        print(f"{Fore.RED}Invalid URL: {url}")
        return
    
    print(f"{Fore.YELLOW}Parsing video URL: {url}")
    
    video_info = parse_video(url)
    
    if not video_info:
        print(f"{Fore.RED}Failed to parse video from URL")
        return
    
    print(f"{Fore.GREEN}Successfully parsed video:")
    print(f"  Title: {video_info.get('title', 'Unknown')}")
    print(f"  Platform: {video_info.get('platform', 'Unknown')}")
    print(f"  Duration: {video_info.get('duration', 0)} seconds")
    
    downloader = VideoDownloader()
    success, path = downloader.download(video_info, output)
    
    if success:
        print(f"{Fore.GREEN}Download completed!")
        print(f"  Saved to: {path}")
    else:
        print(f"{Fore.RED}Download failed: {path}")

@cli.command('batch')
@click.argument('file')
@click.option('--output', '-o', help='Output directory')
def batch_command(file, output):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        urls = extract_urls(content)
        
        if not urls:
            print(f"{Fore.RED}No URLs found in the file")
            return
        
        print(f"{Fore.YELLOW}Found {len(urls)} URLs to process")
        
        downloader = VideoDownloader()
        video_info_list = []
        
        for url in urls:
            if is_valid_url(url):
                print(f"\nParsing: {url}")
                video_info = parse_video(url)
                if video_info:
                    video_info_list.append(video_info)
                    print(f"  {Fore.GREEN}✓ {video_info.get('title', 'Unknown')}")
                else:
                    print(f"  {Fore.RED}✗ Failed to parse")
        
        if video_info_list:
            print(f"\n{Fore.YELLOW}Starting batch download...")
            results = downloader.download_batch(video_info_list, output)
            
            success_count = sum(1 for r in results if r['success'])
            print(f"\n{Fore.GREEN}Batch download completed!")
            print(f"  Success: {success_count}/{len(results)}")
        else:
            print(f"{Fore.RED}No valid videos found")
    
    except FileNotFoundError:
        print(f"{Fore.RED}File not found: {file}")
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}")

@cli.command('parse')
@click.argument('url')
def parse_command(url):
    if not is_valid_url(url):
        print(f"{Fore.RED}Invalid URL: {url}")
        return
    
    print(f"{Fore.YELLOW}Parsing video URL: {url}")
    video_info = parse_video(url)
    
    if video_info:
        print(f"{Fore.GREEN}Video information:")
        print(f"  Title: {video_info.get('title', 'Unknown')}")
        print(f"  Platform: {video_info.get('platform', 'Unknown')}")
        print(f"  Duration: {video_info.get('duration', 0)} seconds")
        print(f"  Download URL: {video_info.get('url', 'Unknown')}")
    else:
        print(f"{Fore.RED}Failed to parse video")

if __name__ == '__main__':
    cli()