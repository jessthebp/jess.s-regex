class WebpageComparer:
    def __init__(self, webpages):
        self.webpages = webpages
        self.num_webpages = len(webpages)
        self.results = defaultdict(lambda: defaultdict(int))

        self._analyze_funcs = [getattr(self, func) for func in dir(self) if func.startswith('_analyze_')]

    def analyze(self):
        print(type(self.webpages))
        print(self.webpages.items())
        for url, content in self.webpages.items():
            print(type(url), type(content))
            print(url)
            for func in self._analyze_funcs:
                print(func)
                if func != self._analyze_https_usage:
                    func(str(content), url)
                else:
                    print(func)
                    func(url)
        return self.results

    def _analyze_headings(self, content, url):
        # Set up heading counts
        self.results[url].setdefault('headings', {})
        self.results[url].setdefault('heading_keywords', {})

        for i in range(1, 7):
            self.results[url]['headings'][i] = 0
            self.results[url]['heading_keywords'].setdefault(i, {'none': 0})
            headings_found = re.findall(r'<h{}>'.format(i), content)
            if not headings_found:
                continue
            else:
                self.results[url]['headings'][i] += 1
                for heading in headings_found:
                    self.results[url]['heading_keywords'][i].setdefault(heading, 0)
                    self.results[url]['heading_keywords'][i][heading] += 1

    def _analyze_links(self, content, url):
        links_found = re.findall(r'<a href=[\'"]?([^\'" >]+)', content)
        self.results[url].setdefault('links', {})
        self.results[url].setdefault('external_links', {})
        self.results[url].setdefault('domains', {})

        for link in links_found:
            if 'http' in link:
                self.results[url]['links'].setdefault(link, 0)
                self.results[url]['links'][link] += 1
                if link not in content:
                    self.results[url]['external_links'].setdefault(link, 0)
                    self.results[url]['external_links'][link] += 1
        # Find links to specific domains
        for link in links_found:
            # Get just the domain
            domain = re.findall(r'(?<=//)[^/]+', link)
            if domain:
                self.results[url]['domains'].setdefault(domain[0], 0)
                self.results[url]['domains'][domain[0]] += 1

    def _analyze_images(self, content, url):
        images_found = re.findall(r'<img (.*?)alt=[\'"]([^\'"]+)', content)
        images_without_alt = re.findall(r'<img .*?alt=[\'"]([^\'"]+)', content)
        srcset_images = re.findall(r'<img .*?srcset=[\'"]([^\'"]+)', content)

        self.results[url].setdefault('images', {})
        self.results[url].setdefault('images_without_alt', {})
        self.results[url].setdefault('srcset_images', {})

        for image in images_found:
            src, alt_text = image
            self.results[url]['images'].setdefault(src, {'alt_text': alt_text, 'count': 0})
            self.results[url]['images'][src]['count'] += 1

        for image in images_without_alt:
            self.results[url]['images_without_alt'].setdefault(image, 0)
            self.results[url]['images_without_alt'][image] += 1

        for image in srcset_images:
            self.results[url]['srcset_images'].setdefault(image, 0)
            self.results[url]['srcset_images'][image] += 1


    def _analyze_addresses_and_phones(self, content, url):
        # address_regex = re.compile(
        #    r'\b\d{5}(?:-\d{4})?\b|[A-Z][a-z.-]+(?: [A-Z][a-z.-]+)?, (?:Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|Wisconsin|Wyoming|AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY)(?:, [A-Z]{2})? \d{5}(?:-\d{4})?|\d+[ ](?:[A-Za-z0-9.-]+[ ]?)+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?')
        phone_regex = re.compile(r'\(?([0-9]{3})\)?([ .-]?)([0-9]{3})\2([0-9]{4})')

          addresses_found = set()
        phones_found = set()
        chunk_size = 10000
        # remove everything above the closing </head> tag
        content = re.sub(r'<head.*?>.*?</head>', '', content, flags=re.DOTALL)

        # remove everything between <script> tags
        content = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL)

        # remove everything between <style> tags
        content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL)

        def chunk_html(content, chunk_size):
            chunks = []
            current_chunk = ""

            # Remove leading/trailing whitespace
            content = content.strip()

            # Split the content into chunks of the specified size
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                chunks.append(chunk)

            return chunks

        chunks = chunk_html(content, chunk_size)

        for chunk in chunks:
            print(chunk)
            # chunk_addresses_found = set(address_regex.findall(chunk))
            chunk_phones_found = set(phone_regex.findall(chunk))
            # addresses_found.update(chunk_addresses_found)
            phones_found.update(chunk_phones_found)

        if not addresses_found:
            print('No addresses found for:', url)
            self.results[url]['addresses'] = {'none': 1}
        else:
            if 'addresses' not in self.results[url]:
                self.results[url]['addresses'] = {}
            for address in addresses_found:
                self.results[url]['addresses'].setdefault(address, 0)
                self.results[url]['addresses'][address] += 1

        if not phones_found:
            print('No phones found for:', url)
            self.results[url]['phones'] = {'none': 1}
        else:
            if 'phones' not in self.results[url]:
                self.results[url]['phones'] = {}
            for phone in phones_found:
                self.results[url]['phones'].setdefault(phone, 0)
                self.results[url]['phones'][phone] += 1
    def _analyze_emails(self, content, url):
        print('Analyzing emails for:', url)
        emails_found = re.findall(r'[\w\.-]+@[\w\.-]+', str(content))
        # remove images with @2x.pong etc
        emails_found = [email for email in emails_found if not email.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if not emails_found:
            print('No emails found for:', url)
            self.results[url]['emails'] = {'none': 1}
        else:
            if 'emails' not in self.results[url]:
                self.results[url]['emails'] = {}
            for email in emails_found:
                self.results[url]['emails'].setdefault(email, 0)
                self.results[url]['emails'][email] += 1

    def _analyze_schema(self, content, url):
        content = bs4.BeautifulSoup(content, 'html.parser')

        self.results[url].setdefault('schema_types', {})
        self.results[url].setdefault('schema_formats', {})

        for script in content('script', type='application/ld+json'):
            try:
                schema = json.loads(script.text)
                if '@type' in schema:
                    self.results[url]['schema_types'].setdefault(schema['@type'], 0)
                    self.results[url]['schema_types'][schema['@type']] += 1

                    if '@context' in schema:
                        self.results[url]['schema_formats'].setdefault(schema['@context'], 0)
                        self.results[url]['schema_formats'][schema['@context']] += 1

            except json.JSONDecodeError:
                pass

    def _analyze_semantic_html(self, content, url):
        semantic_tags = ['header', 'nav', 'main', 'footer']
        self.results[url].setdefault('semantic_elements', {})

        for tag in semantic_tags:
            elements_found = re.findall(r'<{}>'.format(tag), str(content))
            if elements_found:
                self.results[url]['semantic_elements'].setdefault(tag, 0)
                self.results[url]['semantic_elements'][tag] += 1

        print('Finished analyzing semantic HTML')

    def _analyze_videos(self, content, url):
        videos_found = re.findall(r'<video .*?>', str(content))
        if not videos_found:
            print('No videos found for:', url)
        else:
            for video in videos_found:
                # get video attributes
                video_attrs = re.findall(r'\b(\w+)\b\s*=\s*("[^"]*"|\'[^\']*\'|\S+)', video)
                for attr in video_attrs:
                    if attr[0] == 'src':
                        src = attr[1].strip('"').strip("'")
                    else:
                        src = video_attrs[0][1].strip('"').strip("'")
                    if src.startswith('//'):
                        src = 'http:' + src
                    elif src.startswith('/'):
                        base_url = re.search(r'<base href="(.*?)"', content)

                    self.results[url]['videos'].setdefault(src, 0)
                    self.results[url]['videos'][src] += 1
        print('finished analyzing videos')

      def _analyze_table_of_contents(self, content, url):
        toc_found = re.findall(r'<(a|div)\s[^>]*class=[\'"]toc[\'"][^>]*>', content, flags=re.IGNORECASE)
        for toc in toc_found:
            # check if it's a link
            if toc.startswith('<a '):
                # get href attribute
                href_attr = re.search(r'href=[\'"]?([^\'" >]+)', toc)
                if href_attr:
                    href = href_attr.group(1)
                    self.results[url]['toc_links'][href] += 1
            # check if it's a div with nested links
            elif toc.startswith('<div '):
                # find all links within the div
                links_found = re.findall(r'<a\s[^>]*>', toc)
                for link in links_found:
                    href_attr = re.search(r'href=[\'"]?([^\'" >]+)', link)
                    if href_attr:
                        href = href_attr.group(1)
                        self.results[url]['toc_links'][href] += 1


    def _analyze_maps(self, content, url):
        maps_found = re.findall(r'<iframe .*?src=[\'"](.*?google\.[a-z]{2,3}(?:\.[a-z]{2,3})?/maps.*?)["\']', content)
        for map_url in maps_found:
            self.results[url]['maps'][map_url] += 1
        print('finished analyzing maps')

    def _analyze_external_scripts(self, content, url):
        scripts_found = re.findall(r'<script .*?src=[\'"](.*?)[\'"]', content)
        # set default values
        if 'external_scripts' not in self.results[url]:
            self.results[url]['external_scripts'] = {}
        if 'local_scripts' not in self.results[url]:
            self.results[url]['local_scripts'] = {}
        # count the number of scripts from each domain

        for script in scripts_found:
            localscripts = 0
            # Check if the script is hosted on an external domain
            if 'http' in script:
                # Get just the domain
                domain = re.findall(r'(?<=//)[^/]+', script)
                # Set default value
                if domain[0] not in self.results[url]['external_scripts']:
                    self.results[url]['external_scripts'][domain[0]] = 1
                else:
                    # Increment the count for this domain
                    self.results[url]['external_scripts'][domain[0]] += 1
            elif script.startswith('//'):
                # Increment the count for local scripts
                localscripts += 1
                self.results[url]['local_scripts'] = localscripts
        print('finished analyzing external scripts')

    def _analyze_social_media_links(self, content, url):
        social_media_icons_found = re.findall(r'<i.*?class=[\'"].*?(fa|fab|fas|far).*?[\'"].*?>', content)
        social_media_links_found = re.findall(r'<a .*?href=[\'"](.*?(facebook|twitter|instagram|linkedin).*?)[\'"]',
                                              content)

        self.results[url].setdefault('social_media_icons', {})
        self.results[url].setdefault('social_media_links', {})

        for icon in social_media_icons_found:
            self.results[url]['social_media_icons'].setdefault(icon, 0)
            self.results[url]['social_media_icons'][icon] += 1

        for link in social_media_links_found:
            # check if it links to facebook, linkedin, twitter, or instagram as a part of the domain
            if ['facebook', 'linkedin', 'twitter', 'instagram'] in link:
                self.results[url]['social_media_links'].setdefault(link, 0)
                self.results[url]['social_media_links'][link] += 1

        print('Finished analyzing social media links')



    def _analyze_https_usage(self, url):
        # does the beginning of the url begin wtih http or https

        if url.startswith('https'):
            self.results[url]['https'] = True
        elif url.startswith('http'):
            self.results[url]['https'] = False
        else:
            self.results[url]['https'] = False
        print('finished analyzing https usage')

    def get_results(self):
        return self.results

    def get_results_json(self):
        return json.dumps(self.results, indent=4)


    def get_results_dataframe(self):
        return pd.DataFrame(self.results)
