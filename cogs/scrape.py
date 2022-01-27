import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import urllib.parse
import re
import math
import asyncio

# HELPER FUNCTION DECLARATIONS
# --------------------------------------------------------------- #
# Replace all whitespace with '+' and make <search> URL-friendly
def format_search(search):
    return urllib.parse.quote(search.replace(' ', '+'))

# Get rid of all non-alphanum characters
# Replace all whitespace with '-'
def format_card_url(card_name):
    # Replace whitespace with hyphens and remove doubled hypen
    new_name = card_name.replace(' ', '-')
    new_name = new_name.replace('-', '', 1)

    # Return correctly formatted card_url
    return re.sub(r'[^a-zA-Z0-9_\-]', '', new_name)

# Return the min of <a> and <b>
def min(a, b):
    return a if a < b else b

# Builds and returns an Embed object for a list of Search Results
def build_search_embed(search_url, ctx, curr_page, search_results):
    # Initialize Embed object
    embed = discord.Embed(title=f'**Search Results**', url=search_url, description='Use `.select <#>` to choose a card.', color=discord.Color.green())
    embed.set_thumbnail(url='https://i2.wp.com/pkmncards.com/wp-content/uploads/clefairy-expedition-crop-1.jpg?resize=150%2C150&ssl=1')
    embed.set_author(name=f'Requested by {ctx.author.display_name}', icon_url=ctx.author.avatar_url)

    # Get necessary info from <search_results>
    size = len(search_results)
    total_pages = math.ceil(size / 10)
    start_ind = (curr_page - 1) * 10
    end_ind = min(((curr_page - 1) * 10 + 10), size)

    # Get list of 10 Pokemon corresponding to <curr_page>
    list = search_results[start_ind:end_ind]

    # Add Pokemon to <embed>
    for i in range(len(list)):
        pokemon_name_args = re.split(' · ', list[i])
        pokemon_name = pokemon_name_args[0]
        pokemon_set = pokemon_name_args[1]
        embed.add_field(name=f'**{(curr_page-1)*10 + (i+1)}** - {pokemon_name}', value=pokemon_set, inline=False)

    # Add footer to show current page
    embed.set_footer(text=f'Page {curr_page}/{total_pages}')

    return embed

# Wraps page-numbers around in a loop
def wrap(curr_page, total_pages):
    if curr_page == 0:
        return total_pages
    elif curr_page > total_pages:
        return 1
    else:
        return curr_page

# Separates <attack> into a list of variables:
# <attack_cost>, <attack_name>, <attack_damage>, and <attack_desc>
#  args[0]        args[1]        args[2]              args[3]
# TODO: Fix if <attack> is missing one of these argumetns
def parse_attack(attack):
    # Separate various fields of attack
    args = re.split(' → | : |\n', attack)
    return args

# Builds and returns an Embed object for a specific Pokemon card
def build_card_embed(ctx, card_url):
    # Initialize BeautifulSoup object with <card_urL>
    req = requests.get(card_url)
    soup = BeautifulSoup(req.content, 'lxml')

    # Get basic Pokemon card info from <card_url>
    pokemon_name = soup.find('span', class_='name').a.text
    pokemon_hp = soup.find('span', class_='hp').a.text
    pokemon_type = soup.find('span', class_='color').a.text
    pokemon_pic = soup.find('a', class_='card-image-link').img['src']

    # <attack_list> is a list of 4-tuples
    attack_list = []

    # Pull list of attack info from <card_url>
    attacks = soup.find('div', class_='tab text').find('div', class_='text').children
    for attack in attacks:
        if attack.name == None:
            continue
        attack_list.append(parse_attack(attack.text))

    # Set <pokemon_weakness> (defaults to 'N/A' if nothing found)
    pokemon_weakness = soup.find('span', class_='weak').a.text

    # Set <pokemon_resistance> (defaults to 'N/A' if nothing found)
    pokemon_resistance = soup.find('span', class_='resist').a.text

    # Set <pokemon_retreat> (defaults to 'N/A' if nothing found)
    pokemon_retreat = soup.find('span', class_='retreat').a.text

    # Set <pokemon_flavortext> (defaults to empty string if nothing found)
    pokemon_flavortext = soup.find('div', class_='flavor minor-text').text

    # Build embed from above info
    embed = discord.Embed(title=f'{pokemon_name}', url=card_url, description=f'**{pokemon_hp}** · **{pokemon_type}**', color=discord.Color.green())
    embed.set_thumbnail(url=pokemon_pic)
    embed.set_author(name=f'Requested by {ctx.author.display_name}', icon_url=ctx.author.avatar_url)

    # TODO: Special formatting for Pokemon attacks

    embed.add_field(name=f'**Weakness:** {pokemon_weakness}', value=f'**Resistance:** {pokemon_resistance}', inline=True)
    embed.add_field(name='\u200b', value=f'**Retreat Cost:** {pokemon_retreat}', inline=True)
    embed.set_footer(text=pokemon_flavortext)

    return embed

# TODO: Finish different embed methods
def build_item_embed(ctx, card_url):
    pass

def build_poketool_embed(ctx, card_url):
    pass

def build_supporter_embed(ctx, card_url):
    pass

def build_stadium_embed(ctx, card_url):
    pass

def build_energy_embed(ctx, card_url):
    pass
# --------------------------------------------------------------- #

# Scrapes HTML file for Pokemon Card info
class Scrape(commands.Cog):

    # Initialize <Scrape> cog
    def __init__(self, client):
        self.client = client

    # Print confirmation that <Scrape> is active
    @commands.Cog.listener()
    async def on_ready(self):
        print('Scrape cog is online.')

    # Put here so the bot doesn't yell at me :^(
    @commands.command()
    async def select(self, ctx):
        pass

    # Search for requested card on pkmncards.com
    @commands.command()
    async def search(self, ctx, *, query):
        # Find webpage to scrape data from
        base_url = 'https://pkmncards.com/'
        search = '?s=' + format_search(query)
        url = base_url + search
        req = requests.get(url)

        # Initialize BeautifulSoup object with <urL>
        soup = BeautifulSoup(req.content, 'lxml')

        # Get total number of pages in search
        num_pages_html = soup.find('span', class_ = 'out-of last-page-link')
        num_pages = int(num_pages_html.string[2:])

        # Store search results into array
        search_results = []
        for i in range(1, num_pages + 1):
            # Get current page of search results
            curr_page = 'page/' + str(i) + '/'
            url = base_url + curr_page + search
            req = requests.get(url)
            soup = BeautifulSoup(req.content, 'lxml')

            # Get all card names off of page and store in <search_results>
            for result in soup.find_all('a', class_ = 'card-image-link'):
                search_results.append(result['title'])

        # Initialize variables for use in Embed object
        search_url = base_url + search
        size = len(search_results)
        curr_page = 1
        total_pages = math.ceil(size / 10)

        # Build an Embed object formatted to max-10 Pokemon
        # Send 1st page of <search_results> as initializer
        embed = build_search_embed(search_url, ctx, curr_page, search_results)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('⬅️')
        await msg.add_reaction('➡️')

        # Check for moving forward through pages
        def add_page(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == '➡️'

        #Check for moving backwards through pages
        def sub_page(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) == '⬅️'

        # Check if User is selecting an element from <search_results>
        def select(m):
            args = m.content.split(' ')
            return args[0] == '.select' and args[1].isdigit() and int(args[1]) <= size

        # Continue showing <search_results> until User types .select <#>
        # Until then, allow User to scroll through <search_results>
        selection = 0
        while True:
            # List of events for bot to wait for
            tasks = [ \
            asyncio.create_task(self.client.wait_for('reaction_add', timeout=60, check=add_page), name='r_add_next'), \
            asyncio.create_task(self.client.wait_for('reaction_remove', timeout=60, check=add_page), name='r_add_next'), \
            asyncio.create_task(self.client.wait_for('reaction_add', timeout=60, check=sub_page), name='r_add_prev'), \
            asyncio.create_task(self.client.wait_for('reaction_remove', timeout=60, check=sub_page), name='r_add_next'), \
            asyncio.create_task(self.client.wait_for('message', timeout=60, check=select), name='select')]

            # Store completed task into <done> and uncompleted tasks into <pending>
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            finished: asyncio.Task = list(done)[0]

            # Cancel tasks which were not completed
            for task in pending:
                try:
                    task.cancel()
                except asyncio.CancelledError:
                    pass

            # Find name of task which was completed
            action = finished.get_name()

            # Allow for TimeoutError to be excepted
            try:
                res = finished.result()
            except asyncio.TimeoutError:
                await msg.edit(content="Message has timed out.")
                return

            # Move to next page of <search_results> w/ wraparound
            if action == 'r_add_next' or action == 'r_sub_next':
                curr_page = wrap((curr_page + 1), total_pages)
                embed = build_search_embed(search_url, ctx, curr_page, search_results)
                await msg.edit(embed=embed)
            # Move to previous page of <search_results> w/ wraparound
            elif action == 'r_add_prev' or action == 'r_sub_prev':
                curr_page = wrap((curr_page - 1), total_pages)
                embed = build_search_embed(search_url, ctx, curr_page, search_results)
                await msg.edit(embed=embed)
            elif action == 'select':
                user_input: discord.Message = res
                args = user_input.content.split(' ')
                selection = (int(args[1]) - 1)
                break

        # Find and output information for specific card
        card_url = 'card/' + format_card_url(search_results[selection])
        url = base_url + card_url
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'lxml', multi_valued_attributes=None)

        # Finds card type of selected card and builds appropriate embed
        type_section = soup.find('div', class_='type-evolves-is')
        card_type = type_section.find('span', title='Type')
        if card_type == 'Pokémon':
           embed = build_card_embed(ctx, url)
        elif card_type == 'Trainer':
            # Check card subtype (Item, Supporter, Stadium)
            card_type = type_section.find('span', title='Sub-Type').a.string
            if card_type == 'Item':
                # Check card subtype (Item, Pokémon Tool)
                card_type = type_section.find_all('span', title='Sub-Type')
                if len(card_type) == 1:
                    embed = build_item_embed(ctx, url)
                elif card_type[1].a.string == 'Pokémon Tool':
                    embed = build_poketool_embed(ctx, url)
            elif card_type == 'Supporter':
                embed = build_supporter_embed(ctx, url)
            elif card_type == 'Stadium':
                embed = build_stadium_embed(ctx, url)
        elif card_type == 'Energy':
            embed = build_energy_embed(ctx, url)

        await msg.edit(embed=embed)
        await msg.clear_reactions()

# Connect cog to main-bot
def setup(client):
    client.add_cog(Scrape(client))
