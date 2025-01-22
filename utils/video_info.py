import re
from typing import Dict, Optional

class VideoInfoParser:
    CODEC_MAP = {
        'HEVC': 'H265', 'X265': 'H265', 'H265': 'H265', 'H.265': 'H265',
        'AVC': 'H264', 'X264': 'H264', 'H264': 'H264', 'H.264': 'H264',
        'VP9': 'VP9', 'VP8': 'VP8',
        'AV1': 'AV1',
        'MPEG-4': 'MP4', 'MPEG-2': 'MPEG-2'
    }

    LANGUAGE_MAP = {
        'eng': '🇬🇧', 'english': '🇬🇧', 'en': '🇬🇧', 'ingles': '🇬🇧', 'anglais': '🇬🇧', 'английский': '🇬🇧', 'engels': '🇬🇧', 'englisch': '🇬🇧',
        'spa': '🇪🇸', 'spanish': '🇪🇸', 'es': '🇪🇸', 'latino': '🇪🇸', 'español': '🇪🇸', 'castellano': '🇪🇸', 'espanol': '🇪🇸', 'lat': '🇪🇸', 'латинский': '🇪🇸', 'latinoamericano': '🇪🇸', 'hispano': '🇪🇸',
        'fre': '🇫🇷', 'french': '🇫🇷', 'fr': '🇫🇷', 'français': '🇫🇷', 'francais': '🇫🇷', 'французский': '🇫🇷', 'franz': '🇫🇷', 'vf': '🇫🇷', 'vff': '🇫🇷',
        'ger': '🇩🇪', 'german': '🇩🇪', 'de': '🇩🇪', 'deutsch': '🇩🇪', 'немецкий': '🇩🇪', 'deu': '🇩🇪', 'deutsche': '🇩🇪',
        'ita': '🇮🇹', 'italian': '🇮🇹', 'it': '🇮🇹', 'italiano': '🇮🇹', 'итальянский': '🇮🇹', 'ital': '🇮🇹',
        'rus': '🇷🇺', 'russian': '🇷🇺', 'ru': '🇷🇺', 'русский': '🇷🇺', 'pусский': '🇷🇺', 'руc': '🇷🇺', 'россия': '🇷🇺',
        'jpn': '🇯🇵', 'japanese': '🇯🇵', 'ja': '🇯🇵', '日本語': '🇯🇵', 'японский': '🇯🇵', 'jap': '🇯🇵', 'japan': '🇯🇵',
        'kor': '🇰🇷', 'korean': '🇰🇷', 'ko': '🇰🇷', '한국어': '🇰🇷', 'корейский': '🇰🇷', 'kor': '🇰🇷', 'korea': '🇰🇷',
        'chi': '🇨🇳', 'chinese': '🇨🇳', 'zh': '🇨🇳', '中文': '🇨🇳', 'китайский': '🇨🇳', 'mandarin': '🇨🇳', 'cn': '🇨🇳', 'hans': '🇨🇳', 'hant': '🇨🇳', 'cantonese': '🇨🇳',
        'hin': '🇮🇳', 'hindi': '🇮🇳', 'hi': '🇮🇳', 'हिन्दी': '🇮🇳', 'хинди': '🇮🇳', 'हिंदी': '🇮🇳',
        'por': '🇵🇹', 'portuguese': '🇵🇹', 'pt': '🇵🇹', 'português': '🇵🇹', 'portugues': '🇵🇹', 'pt-br': '🇵🇹', 'ptbr': '🇵🇹', 'brazilian': '🇵🇹', 'brasil': '🇵🇹', 'br': '🇵🇹', 'português-br': '🇵🇹',
        'pol': '🇵🇱', 'polish': '🇵🇱', 'pl': '🇵🇱', 'polski': '🇵🇱', 'польский': '🇵🇱', 'polskie': '🇵🇱', 'pol': '🇵🇱',
        'dut': '🇳🇱', 'dutch': '🇳🇱', 'nl': '🇳🇱', 'nederlands': '🇳🇱', 'голландский': '🇳🇱', 'flemish': '🇳🇱', 'vlaams': '🇳🇱', 'hollands': '🇳🇱',
        'dan': '🇩🇰', 'danish': '🇩🇰', 'da': '🇩🇰', 'dansk': '🇩🇰', 'датский': '🇩🇰', 'dan': '🇩🇰',
        'fin': '🇫🇮', 'finnish': '🇫🇮', 'fi': '🇫🇮', 'suomi': '🇫🇮', 'финский': '🇫🇮', 'suomalainen': '🇫🇮',
        'nor': '🇳🇴', 'norwegian': '🇳🇴', 'no': '🇳🇴', 'norsk': '🇳🇴', 'норвежский': '🇳🇴', 'nob': '🇳🇴', 'nno': '🇳🇴',
        'swe': '🇸🇪', 'swedish': '🇸🇪', 'sv': '🇸🇪', 'svenska': '🇸🇪', 'шведский': '🇸🇪', 'swe': '🇸🇪',
        'tur': '🇹🇷', 'turkish': '🇹🇷', 'tr': '🇹🇷', 'türkçe': '🇹🇷', 'turkce': '🇹🇷', 'турецкий': '🇹🇷', 'turk': '🇹🇷',
        'ara': '🇸🇦', 'arabic': '🇸🇦', 'ar': '🇸🇦', 'عربى': '🇸🇦', 'арабский': '🇸🇦', 'عربي': '🇸🇦', 'arab': '🇸🇦',
        'tha': '🇹🇭', 'thai': '🇹🇭', 'th': '🇹🇭', 'ไทย': '🇹🇭', 'тайский': '🇹🇭', 'thai': '🇹🇭',
        'vie': '🇻🇳', 'vietnamese': '🇻🇳', 'vi': '🇻🇳', 'tiếng việt': '🇻🇳', 'вьетнамский': '🇻🇳', 'tieng viet': '🇻🇳',
        'ind': '🇮🇩', 'indonesian': '🇮🇩', 'id': '🇮🇩', 'bahasa': '🇮🇩', 'индонезийский': '🇮🇩', 'indo': '🇮🇩',
        'ukr': '🇺🇦', 'ukrainian': '🇺🇦', 'uk': '🇺🇦', 'українська': '🇺🇦', 'украинский': '🇺🇦', 'ukr': '🇺🇦',
        'heb': '🇮🇱', 'hebrew': '🇮🇱', 'he': '🇮🇱', 'עברית': '🇮🇱', 'иврит': '🇮🇱', 'heb': '🇮🇱',
        'gre': '🇬🇷', 'greek': '🇬🇷', 'el': '🇬🇷', 'ελληνικά': '🇬🇷', 'греческий': '🇬🇷', 'gre': '🇬🇷'
    }

    QUALITY_MAP = {
        'WEBDL': 'WEB-DL', 'WEB-RIP': 'WEBRip', 'WEBRIP': 'WEBRip',
        'BLURAY': 'BluRay', 'BLU-RAY': 'BluRay', 'BDRIP': 'BluRay',
        'HDTV': 'HDTV',
        'CAMRIP': 'CAM', 'CAM-RIP': 'CAM', 'HDCAM': 'HDCAM',
        'DVDRIP': 'DVDRip', 'DVD-RIP': 'DVDRip',
        'TELESYNC': 'TS', 'TELE-SYNC': 'TS',
        'PROPER': 'PROPER', 'REPACK': 'REPACK'
    }

    HDR_MAP = {
        'DOLBYVISION': 'DV', 'DOLBY-VISION': 'DV', 'DV': 'DV',
        'HDR10PLUS': 'HDR10+', 'HDR10+': 'HDR10+', 'HDR10P': 'HDR10+',
        'HDR10': 'HDR10',
        'HDR': 'HDR',
        'HLG': 'HLG'
    }

    HDR_PRIORITY = {
        'HDR': 1,
        'HDR10': 2,
        'HDR10+': 3,
        'DV': 4
    }

    AUDIO_MAP = {
        'DOLBYATMOS': 'Atmos', 'ATMOS': 'Atmos',
        'TRUEHD': 'TrueHD', 'TRUE-HD': 'TrueHD',
        'DTS-HD': 'DTS-HD', 'DTSHD': 'DTS-HD',
        'DTS': 'DTS',
        'DOLBYDIGITALPLUS': 'DD+', 'DOLBYDIGITAL+': 'DD+', 'DDP': 'DD+', 'EAC3': 'DD+', 'E-AC3': 'DD+',
        'DOLBYDIGITAL': 'DD', 'AC3': 'DD', 'AC-3': 'DD',
        'AAC': 'AAC',
        'MP3': 'MP3'
    }

    AUDIO_PRIORITY = {
        'MP3': 1,
        'AAC': 2,
        'DD': 3,
        'DD+': 4,
        'DTS': 5,
        'DTS-HD': 6,
        'TrueHD': 7,
        'Atmos': 8
    }

    CODEC_PRIORITY = {
        'MP4': 1,
        'MPEG-2': 2,
        'VP8': 3,
        'H264': 4,
        'VP9': 5,
        'H265': 6,
        'AV1': 7
    }

    RESOLUTION_PRIORITY = {
        '360p': 1,
        '480p': 2,
        '720p': 3,
        '1080p': 4,
        '4K': 5,
        '8K': 6
    }

    RESOLUTION_PATTERNS = [
        r'(?i)\b(4320|2160|1080|720|480|360)p?\b',
        r'(?i)\b(8K|4K|2K|UHD|FHD|HD|SD)\b',
    ]

    QUALITY_PATTERNS = [
        r'(?i)\b(WEB-?DL|WEB-?RIP|BLU-?RAY|HDTV|CAM-?RIP|HDCAM|DVD-?RIP)\b',
        r'(?i)\b(TELESYNC|(?<![A-Z0-9])TS(?![A-Z0-9]))\b',
        r'(?i)\b(PROPER|REPACK)\b',
    ]

    CODEC_PATTERNS = [
        r'(?i)\b(?:HEVC|(?:x|h)\.?265|(?:x|h)\.?264|AVC|MPEG-[24]|VP[89]|AV1)\b',
        r'(?i)(10bit|10-bit|8bit|8-bit)',
    ]

    HDR_PATTERNS = [
        r'(?i)(HDR10\+|HDR10|DOLBY\s*VISION|DOLBY-?VISION|\bDV\b|HDR|HLG)',
    ]

    AUDIO_PATTERNS = [
        r'(?i)(DD\+?[257]\.1|E-?AC-?3|DDP?[257]\.1|DOLBY\s*DIGITAL\s*(?:PLUS|\+)?\s*(?:[257]\.1)?)',
        r'(?i)(DTS(?:-(?:HD|X|ES|MA))?(?:\s*[257]\.1)?)',
        r'(?i)(DOLBY\s*ATMOS|TRUEHD(?:\s*[257]\.1)?)',
        r'(?i)(AAC(?:[257]\.1)?|MP3|AC-?3)',
        r'(?i)(?<!\d)([257]\.1)(?:\s*CH(?:ANNEL)?)?(?!\.\d)',
    ]

    LANGUAGE_PATTERNS = [
        r'(?i)\b(eng(?:lish)?|spa(?:nish)?|fre(?:nch)?|ger(?:man)?|ita(?:lian)?|rus(?:sian)?|jpn|japanese|kor(?:ean)?|chi(?:nese)?|hin(?:di)?|por(?:tuguese)?|pol(?:ish)?|dut(?:ch)?|dan(?:ish)?|fin(?:nish)?|nor(?:wegian)?|swe(?:dish)?|tur(?:kish)?|ara(?:bic)?|tha(?:i)?|vie(?:tnamese)?|ind(?:onesian)?|ukr(?:ainian)?|heb(?:rew)?|gre(?:ek)?)\b',
        r'(?i)(🇺🇸|🇬🇧|🇪🇸|🇫🇷|🇩🇪|🇮🇹|🇷🇺|🇯🇵|🇰🇷|🇨🇳|🇮🇳|🇵🇹|🇵🇱|🇳🇱|🇩🇰|🇫🇮|🇳🇴|🇸🇪|🇹🇷|🇸🇦|🇹🇭|🇻🇳|🇮🇩|🇺🇦|🇮🇱|🇬🇷)',
    ]

    SIZE_PATTERNS = [
        r'(?i)(?:size)?[:\s]*(\d+(?:\.\d+)?)\s*([KMGT]i?B)',
        r'(?i)(\d+(?:\.\d+)?)\s*(?:GB|GiB|MB|MiB|TB|TiB|KB|KiB)',
    ]

    @staticmethod
    def clean_text(text: str) -> str:
        return ' '.join(text.split())

    @staticmethod
    def find_pattern(text: str, patterns: list) -> Optional[str]:
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        return None

    @staticmethod
    def find_all_patterns(text: str, patterns: list) -> list:
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, text))
        return list(set(matches))

    @staticmethod
    def parse_size_text(text: str) -> Optional[float]:
        size_map = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
        
        for pattern in VideoInfoParser.SIZE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                try:
                    size = float(match.group(1))
                    unit = match.group(2)[:2].upper()
                    if unit in size_map:
                        return size * size_map[unit]
                except (ValueError, IndexError):
                    continue
        return None

    @staticmethod
    def format_size(size_bytes: int) -> str:
        if not size_bytes:
            return None
        try:
            size_bytes = float(size_bytes)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_bytes < 1024:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.2f} PB"
        except (ValueError, TypeError):
            return None

    def normalize_resolution(self, resolution: str) -> str:
        if not resolution or resolution == 'Unknown':
            return 'Unknown'
            
        # Clean the input string
        resolution = resolution.upper().replace(' ', '').replace('-', '')
        
        # Convert common terms to their numeric resolution
        if resolution in ['HD', 'HDRIP', 'HDRIP']:
            return '720p'
        if resolution in ['SD', 'SDRIP']:
            return '480p'
        if resolution in ['FHD']:
            return '1080p'
        if resolution in ['UHD', '4K']:
            return '4K'
        if resolution in ['8K']:
            return '8K'
            
        # Check for numeric resolutions
        numeric_match = re.search(r'(?i)\b(4320|2160|1080|720|480|360)p?\b', resolution)
        if numeric_match:
            base = numeric_match.group(1)
            if base == '4320':
                return '8K'
            if base == '2160':
                return '4K'
            return f"{base}p"
            
        return resolution

    def normalize_hdr(self, hdr: str) -> str:
        if not hdr:
            return None
        hdr = hdr.upper().replace(' ', '')
        return self.HDR_MAP.get(hdr, hdr)

    def normalize_audio(self, audio: str) -> str:
        if not audio or audio == 'Unknown':
            return 'Unknown'

        audio = audio.upper().replace(' ', '')

        normalized = self.AUDIO_MAP.get(audio)
        if normalized:
            return normalized

        channels = re.search(r'(?<!\d)([257]\.1)(?!\.\d)', audio)
        if channels:
            return f"{channels.group(1)} CH"
        
        return audio

    def normalize_quality(self, quality: str) -> str:
        """Convert quality to consistent format."""
        if not quality or quality == 'Unknown':
            return 'Unknown'
        quality = quality.upper().replace(' ', '')
        return self.QUALITY_MAP.get(quality, quality)

    def normalize_languages(self, languages: list) -> list:
        """Convert language codes/names to flags."""
        if not languages or languages == ['Unknown']:
            return ['Unknown']
        
        flags = set()
        for lang in languages:
            if any(x in lang.lower() for x in ['multi', 'dual', 'triple']):
                continue
            
            if any(flag in lang for flag in self.LANGUAGE_MAP.values()):
                flags.add(lang)
                continue
            
            lang_lower = lang.lower()
            flag = self.LANGUAGE_MAP.get(lang_lower)
            if flag:
                flags.add(flag)
        
        return sorted(list(flags)) if flags else ['Unknown']

    def normalize_codec(self, codec: str) -> str:
        if not codec or codec == 'Unknown':
            return 'Unknown'
        codec = codec.upper().replace(' ', '')
        
        # Normalize bit format first
        for bit in ['10', '8', '12']:
            if f'{bit}BIT' in codec or f'{bit}-BIT' in codec:
                codec = codec.replace(f'{bit}BIT', '').replace(f'{bit}-BIT', '')
                normalized = self.CODEC_MAP.get(codec, codec)
                return f"{normalized}{' ' if normalized else ''}{bit}-bit"
            
        return self.CODEC_MAP.get(codec, codec)

    def sort_hdr_formats(self, formats: list) -> list:
        return sorted(formats, key=lambda x: self.HDR_PRIORITY.get(x, 999))

    def sort_audio_formats(self, formats: list) -> list:
        return sorted(formats, key=lambda x: self.AUDIO_PRIORITY.get(x.split()[0], 0))

    def sort_codecs(self, codecs: list) -> list:
        return sorted(codecs, key=lambda x: self.CODEC_PRIORITY.get(x, 0))

    def sort_resolutions(self, resolutions: list) -> list:
        return sorted(resolutions, key=lambda x: self.RESOLUTION_PRIORITY.get(x, 0))

    def parse(self, stream: Dict) -> Dict[str, str]:
        text = ' '.join(filter(None, [
            stream.get('title', ''),
            stream.get('description', ''),
            stream.get('torrentTitle', ''),
            stream.get('behaviorHints', {}).get('filename', '')
        ]))
        text = self.clean_text(text)
        name = stream.get('name', '')

        # Extract languages and resolutions from name and text
        name_languages = self.normalize_languages(self.find_all_patterns(name, self.LANGUAGE_PATTERNS))
        text_languages = self.normalize_languages(self.find_all_patterns(text, self.LANGUAGE_PATTERNS))
        languages = list(dict.fromkeys(name_languages + text_languages))
        if languages == []:
            languages = ['Unknown']

        name_resolutions = [self.normalize_resolution(r) for r in self.find_all_patterns(name, self.RESOLUTION_PATTERNS)]
        text_resolutions = [self.normalize_resolution(r) for r in self.find_all_patterns(text, self.RESOLUTION_PATTERNS)]
        resolutions = list(filter(lambda x: x != 'Unknown', dict.fromkeys(name_resolutions + text_resolutions)))
        resolutions = self.sort_resolutions(resolutions)
        resolution = resolutions[-1] if resolutions else 'Unknown'
        
        size = stream.get('size', 0) or stream.get('torrentSize', 0) or \
               stream.get('behaviorHints', {}).get('videoSize', 0)
        
        if not size:
            size = self.parse_size_text(text)

        quality = self.normalize_quality(self.find_pattern(text, self.QUALITY_PATTERNS))
        
        codecs = [self.normalize_codec(c) for c in self.find_all_patterns(text, self.CODEC_PATTERNS)]
        codecs = list(filter(lambda x: x != 'Unknown', dict.fromkeys(codecs)))
        codecs = self.sort_codecs(codecs)
        codec = codecs[-1] if codecs else 'Unknown'

        hdr_formats = [self.normalize_hdr(h) for h in self.find_all_patterns(text, self.HDR_PATTERNS)]
        hdr_formats = list(filter(None, dict.fromkeys(hdr_formats)))
        hdr_formats = self.sort_hdr_formats(hdr_formats)
        
        audio_formats = [self.normalize_audio(a) for a in self.find_all_patterns(text, self.AUDIO_PATTERNS)]
        audio_formats = list(filter(lambda x: x != 'Unknown', dict.fromkeys(audio_formats)))
        audio_formats = self.sort_audio_formats(audio_formats)
        
        info = {
            'resolution': resolution,
            'quality': quality,
            'codec': codec,
            'hdr': hdr_formats,
            'audio': audio_formats,
            'languages': languages,
            'size': self.format_size(size) if size else None,
            'is_cached': stream.get('is_cached', False)
        }

        description = []
        if info['resolution']:
            description.append(f"📺 {info['resolution']}")

        if info['quality'] != 'Unknown':
            description.append(f"🎞️ {info['quality']}")

        if info['codec'] != 'Unknown':
            description.append(f"⚙️ {info['codec']}")

        if info['hdr']:
            description.append(f"✨ {', '.join(info['hdr'])}")

        if info['audio']:
            description.append(f"🔊 {', '.join(info['audio'])}")

        if info['languages']:
            display_languages = [lang for lang in info['languages'] if lang != 'Unknown']
            if display_languages:
                description.append(f"🎙️ {', '.join(display_languages)}")
        
        if info['size']:
            description.append(f"💾 {info['size']}")
        
        if not info['is_cached']:
            description.append("⚠️ Instant streaming unavailable")

        return {
            'raw_info': info,
            'formatted_description': '\n'.join(description)
        }
