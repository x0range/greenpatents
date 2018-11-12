# prototype

# from https://stackoverflow.com/questions/48897635/given-a-geographical-coordinate-in-u-s-how-to-find-out-if-it-is-in-urban-or-ru
# with shapefile from https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-urban-area/

import shapefile
from shapely.geometry import Point 
from shapely.geometry import shape 
import numpy as np
import pandas as pd
import sys
import pdb
import os
import pickle


class AssigneeDataParser():
    def __init__(self):
        """prepare geo-lookup for urben/rural"""
        self.shp = shapefile.Reader('ne_10m_urban_areas.shp') #open the shapefile
        self.all_shapes = self.shp.shapes() # get all the polygons
        self.temp_save_name = "patents_table_tempsave.pkl"
        self.table_save_name = "patents_table.pkl"
        
        """reload or prepare variables"""
        
        if os.path.exists(self.temp_save_name):
            with open(self.temp_save_name, "rb") as sfile:
                self.assigneeDict, self.patentDict, self.locationsDict = pickle.load(sfile)
        else:
            self.assigneeDict = {}
            self.patentDict = {}
            self.locationsDict = {}
    
    def tempsave(self):
        save_list = [self.assigneeDict, self.patentDict, self.locationsDict]
        with open(self.temp_save_name, "wb") as sfile:
             pickle.dump(save_list, sfile, protocol=pickle.HIGHEST_PROTOCOL)
        
    def is_urban(self, pt):       
        """Method to identify rural/urban status corresponding to pair of coordinates.
           Adapted from https://stackoverflow.com/questions/48897635
            Arguments:
                pt - tuple - coordinates (Latitude, Longitude)
            Returnd:
                bool - is this an urban place"""
        pt = (pt[1], pt[0]) # reverse coordinate order
        result = False
        for current_shape in self.all_shapes:
            if not result:
                result = Point(pt).within(shape(current_shape))
        #print (pt, result)
        return result

    def parse_locations(self, sourcefile="location.tsv"):
        """Method to parse locations. Populates location dict"""
        count = 0
        with open(sourcefile, "r") as ifile:
            _ = ifile.readline()
            for line in ifile:
                count += 1
                print(count, end="\r")
                elementi = line.split("\t")
                locID, locCountry, locState, locLat, locLong = elementi[0], elementi[3], elementi[2], float(elementi[4]), float(elementi[5])
                locIsUrban = self.is_urban((locLat, locLong))
                
                """ attach to dict"""
                self.locationsDict[locID] = {"urban": locIsUrban, "country": locCountry, "state": locState, "latitude": locLat, "longitude": locLong}       

    def parse_location_assignee_correspondence(self, sourcefile="location_assignee.tsv"):
        """Method to parse assignee-location correspondence. Populates assignee dict with 
           corresponding location data."""
        count = 0
        with open(sourcefile, "r") as ifile:
            _ = ifile.readline()
            for line in ifile:
                count += 1
                print(count, end="\r")
                elementi = line.split("\t")
                locID, assigneeID = elementi[0], elementi[1].replace("\n", "")
                
                """ match """
                unresolvable_assignees = ['', 'svuy3fwvcv2t', '7tl6t1hjfbjm', '7qi19h4dr2jg', '4mghocpfq5il', '8igd0fwa1myk', 'prg3gqqpt0rq', '3qux6qk686vn', 'p7lqdjzk8ztt', 'hiqp7a3fl2yp', 'ugtj4q7nwv7y', 'hkebf0e7kgtr', '9wmsxd3tyo9s', '51ukw5w7mll2', 'vrtwnv758esl', 'a9v7dt0v2c54', '6ctwtm63qqi8', 'cxe6uli6urfw', 'agxq076ou08j', 'fsye5jw3xotw', 'dm4h7olzz1h1', 'b0ciop4ki2yc', 'z5qesjj3rjha', 'jdttuaegfv7e']
                if locID not in unresolvable_assignees:
                    self.assigneeDict[assigneeID] = self.locationsDict[locID]
                else:
                    self.assigneeDict[assigneeID] = {"urban": None, "country": None, "state": None, "latitude": np.nan, "longitude": np.nan} 

            
    def parse_assignee(self, sourcefile="assignee.tsv"):
        """Method to parse assignee data. Populates assignee dict with all except location."""
        count = 0
        with open(sourcefile, "r") as ifile:
            _ = ifile.readline()
            for line in ifile:
                count += 1
                print(count, end="\r")
                elementi = line.split("\t")
                assigneeID, assigneeType, assigneeName = elementi[0], int(elementi[1]), elementi[4].replace("\n", "")
                """Assignee types are:
                        2 - US Company or Corporation, 
                        3 - Foreign Company or Corporation, 
                        4 - US Individual, 
                        5 - Foreign Individual, 
                        6 - US Government, 
                        7 - Foreign Government, 
                        8 - Country Government, 
                        9 - State Government (US). 
                        Note: A "1" appearing before any of these codes signifies part interest)
                   Universities count as private. Therefore that needs to be scraped out of the Names.
                    """
                
                """keyword search of assignee name to identify universities, research institutes etc. as non-private"""
                isPrivate = True
                company_cindicating_terms = ["Ltda.", "Ltd.", "S.a.r.l.", "LLC", "GmbH", "GBR", "Inc.", "Private Inst",  
                                             "Co.", "S.A.", "S.a.S.", "S.p.A.", "S.n.c.", "S.a.p.a.", "SNC", "SARL", 
                                             "A.G.", "Company", "Corp.", "INC", "L.L.C.", "S.L.", "S.r.l.", "AG"]
                university_indicating_terms = ["Universit",  "universit", "Ecole", "Escuel", "Hochschule", 
                                               "hochschul", "Regent", "Univ.", "Akadem"]
                if (assigneeType in [6, 7, 8, 9]):
                    isPrivate = False
                elif any(st in assigneeName for st in university_indicating_terms):       # use terms from Nanda et al
                    isPrivate = False
                elif any(st in assigneeName for st in ["Inst.", "Institut", "Academ"]) and \
                                not any(st in assigneeName for st in company_cindicating_terms):
                    isPrivate = False
                
                """ match """ 
                unresolvable_assignees = ['005a14a3f623fda683a42aeff707130b', '00f32913a4f6a241542885eecf895707', '019d6c70c2b179266a30a84df2a0521d', '01a28790d00788ab080dcbf63f822f79', '01af47874882e91cf7376379eb315f8c', '01b7ffaeec621e9de9bfc9c76a6b4075', '01cec735d54b40cdced6125d8876591f', '01d561a71b98ee5bea0f87fdb64628f6', '0202a0089f7004428ab6124487ee88cd', '02891c5f7fa00dff48abc32b594feb8d', '02bb1b82e1e936d881894f8d9d1909d1', '0316533dbfeb3bc5a479c9ad8bba12ae', '035602c1e74bda4e5254bbcdddb9b7e7', '036219590c7560475ef23717489f7879', '038ede09b0f75a94773287fd8d73b9c4', '03de5d25e6f6155766bfabddbe52b41b', '043daa78eb5ddaeb07897841b15448c1', '057e08423fd98414944077ddc68ea167', '05d6740ac4d68aa70f2170a82f73be03', '06034182aee866077e2b85b96b221108', '06738066dd7f7bf7d17165310daf6725', '069513b014bdf057320d5adf34a43908', '06a2aedda80828a106637d60c0bcb359', '06c03d16c4b496dd22ab1ff88040653d', '06c66c1b4bf203cf6bdbbc5cf8cf60f3', '06e069fc4d2a3ded6460f2d747bc33e2', '08027d3aa7d203946cf0f2444add6cac', '082e2995473daefc03b98a37a599bb7f', '089ec53d6b6856a3d65bb913f4163206', '08e1ef0011f7f609b92130e3cf9a024f', '0934b064a781bddf28f0d85cd4ac26c2', '0943363e860e80a8ca39e12407911fac', '0952506c4cb97a48528b716c2f5a4b0b', '09a8ca74f7c6f4678b6288fd347472ee', '09c1b61cdaf46f6ee1dd842ae7b50008', '09cb8015b8cae0d76d0b708c098f5a10', '0a2fe07a27cde349ce5f6209da41584f', '0a6256a27d6ff442b5093444a1b90f50', '0a78c1c512b4b9b42132aa4299b65e04', '0a91f73f02671d3646f8be8aab98de4a', '0afc6c599e0f9220d7df7040e552bf96', '0beb3fe4c4ef4ac4ecf1bc0ca7ec45de', '0bf108aa33c8cfe64ba4bf9032fe3f53', '0c4d3b8c01e3b18ecd69438479c63429', '0d11c1fd24b8994f53996d8b3d8398b0', '0d65c91081f9d614eecd19bc18441b02', '0d8b645239681025a3b48439888a6ccf', '0d9176c78cb23665bf4a693642b4a0fe', '0e8c25d705645fd4a25813c67e63a723', '0e9572f38e3514bbc0ee6a8592bb3e67', '0ecf329b27e7fe448b74ed1941c1677d', '0f23f1aa8f20279371facffbd6acdac0', '0f263d9a7e24b18ce0acaf042d395d34', '0f34a4ca5078508e745d86209bcff157', '0f4cf84fa130f7587700b71402fd28f2', '0f5bd66d0fd0d500a210f18ae99614cb', '0f8b0dff5dee1a028b0c84aed149ab8f', '10b0b5d19c17d04ff01aa0e4b4e16afb', '10c94f50b9fb5e716f81c232d0327ac9', '113087cc109f74e15f94500cbc384dca', '1156762d6832ea730c7d7cf50a334ef8', '119c2c3e3b5e3a2101174b7b1299218e', '1243ce1e370e55575b1d34012e4023a7', '13acac43bc3e8f25ca0b065cda14cec2', '13b2ce248eb1d876df7bbd20fa1403c0', '142f40b030d697ead5d67f9869990d13', '145ebd07cd64bd3cceaf8d099e583f73', '14da95180316647372766f4b0c973cd4', '152e513051cda9d37ecd3ad1694e8216', '156c2b75f3356bad623b3ab24aa1da4c', '161b84475b5dfc0610782f5ec6a6ed77', '16a98063898a48e6f65f605624d19c01', '1746260c332cc83a137c058c25b996be', '176dd9c19e2672c4426e9bb2cd2b0dd8', '179c13dccf052d0ff93594925f6dd035', '17afd77ad44dcd09ce0c814365f88eed', '17b71ad5f69721428f4f35cb68150bdf', '17c6953b827b0e7d9a03780a6da869af', '17cd80eb03e941a3b71bdb95f9140313', '180200f2008c35c52ccdf92ee7450036', '1834eeacf4d4d0d3044fba70e371a660', '186829fb63a637898337941f26948d10', '187d4a41aebd2689d933a39ba244be2c', '18fd4cfbceb6a6439bd8263a0352fb84', '1966fac05a62fd5f0d5467ee58e8a1e8', '1975c91d1e96156a39fd684ce797ff47', '19e60b8a5e49acfe8c4989c7fe51f069', '1a8a40c04ed588e1d7d1d642d33dcf80', '1ae894aee2e88727c30d62e817b9d577', '1b06416f9d79932bac04a3f0dce57a6c', '1b54280690b85d7e5ccfdecf5cfcd13d', '1bceb8b9b94d83fe734a474fee08cbef', '1bd18b2ab384ecb3f94ccbc14eecce5b', '1c23686281e79f976fbc8ba372afc3f5', '1c482867e59cef893db1d2c2d5cf3d15', '1ca258403d62fc519e8fd017c7d0eebf', '1cdb43675d1e6a629a3d4b67283b7d27', '1cfd3add4a2e30e1190fa4303ec6894e', '1d1883fe2a2df078c20d7df1f7af4183', '1d31850f9932818773e8a73c39f403c9', '1e61db75017edae0b06e300ea2c889f5', '1e6a398ad46eea1059e571ec6a746e6d', '1e7a5aa0f19e8d0702a2eef2acb709c5', '1eb9c4071848056bc6410170ed16147f', '1ee93f90341262fe999f0ad68d796694', '1f609384735c83194bd17b2a6cc2615f', '1ffe673c8b85cbd0f5764ec654898fec', '20fcc0afe83098fcdcb80a7322482b47', '21760bf4995f534d857a279a0491b1ed', '21c8089f8580ca87eef1aac2d23ad7e4', '22551073ff7ec5f3189817830e86442c', '22926dbb6c02738495e04c3ec45fdbbd', '22e468addf6ed2683fa18e450fb7d1ed', '23946622f1abb8efab4911bb38c57ce3', '23b0878e705deaf7deb5d10d3c18425c', '23d296f3f8023830dd446ff5aad0b3cf', '2490d7891bf5d775ab92e5c29602d3e6', '24a188f843593e834d9453f7b23e3a86', '24b56fde81a2f2d0aa8bc0425afc2dec', '24e4674313aa19e9dbd95324f0861116', '25931b7d7bb2d20cb3980ad7f5f09125', '25cc063c9e5147d4e0ba519b6abd36e7', '26017840aeb0ed16fadfb6241578c3a3', '2644da9deb367ae4671b471d134ac9ba', '26ef6147c94094676979f64e59a911a3', '2770b44a1e0b7fa8b457b96004e9bb4a', '2777278d97013ef0e6c3b7b1987c9ee5', '27accf06fba9fe6ef29dc696b914d244', '27f4d64fc0e115148c90ff0cd23209dd', '289456362eb66d1ae1318a8333a2bfaa', '28ce388ab7c06bb4f27c1d9d5b90a4c1', '29007afb3e6c1cdaf2ac74edd659b5cb', '291c00bb26d4dfe75b6e58baa36abd01', '296fe06bd032dcbc8d793e5b08ee75e0', '29b27c5a3b841ed41c6ed987f5767d9b', '2a635ad050d0d72de14727d71cffae7b', '2abb07024bbc0534e2cd8f852f19458f', '2aee44fb263e8c112e5d4833bab1f321', '2b2c63134a32102286c2b908aed248a4', '2b69938cd026ef6718afdd7aa7656d14', '2b9af3e807f03a261b45d34d61f9e11f', '2c450c91ee347025d077c6f0b4bf12d8', '2d2a24ca7dcdc348a2b44711e6f7549a', '2d3202b5a6a94107ca1bad33bee88d28', '2d53ae4ded97464fb883fcb4353226f8', '2e4c04d8f6ce0f4bc9dc9e2d347f9df9', '2f1c770887895852f21c4cd4cc7073fa', '2f1efd056a515f5d0769057f48e3757a', '2f25851d14a9490846b5049f52ea3960', '307b4d40af53f01f6c2bc1c50749d767', '30a8999b94f7681c52a6f259faad8a87', '30edd40c2983d449d126a46b7a72f257', '318fe04ce51a07ba7832365bb582944c', '31bb58607f629d8acb5ddbd8771b4aca', '31bcdf9f49b7b52244e6cfa67d4d5db5', '32251edf0d1190032fa6730cbeb10d35', '32aa8f7cf8852518f87fd920b368cbe3', '33f7aa90ead059560fadedd9f59a5929', '34ab8ff575ba389f5c8fc5d9d0b8260b', '34e028f30981e2f307985a6a1c4d01bd', '35208c9d65e4aabe1bd55039b439ca9f', '357e72f206abf85399558a2fdbbc0aa3', '3613a649e07babd692cc95b75fb4f584', '365235fcf9a6b0aa0dc8e141a184b8c0', '36ae611ea28c5868d70881c102f45bc5', '3730dfe4c0de3ca8d7e315ae5be3252a', '37631a8d9ab6fbba700ced22642678fb', '376ee7a1dd1be502b20e99eb95f2447c', '37d87d3d6727d3b8ecae88a25727fdce', '38c58dceeb7a75bd77ebd6722eb4e9bc', '390d17e78bcb65aebec04e80f1dc5b18', '39133894ba1c68addd5299dda8b8d9ce', '391cdfdca836ba533b120a9aeadfea7c', '395f156648925e251789a63a9ee857b7', '396b783a053902c80a03b580ce84909c', '39a9f8c0beda723727ef398f601752dd', '39c728c47cd9dbd012c68940226e4f9e', '39d19e66f7f1910177ab8d69006c9f13', '39e5be4db6ee6bbcbf70b5a5a8455f4a', '3a0b555453b6d7919164414b686e4452', '3a3999a38e0d79bc9058cb24c7f8cdbd', '3abb2ba73db3ea472cd9f0c2100c5849', '3ad61684498292de2331eb3cc002bb6f', '3b209d39bcef7dab866cb672b54d00fe', '3b288b7194c22e39bc3b90eeea74b048', '3b2a8ae4bfb370c92a5092bdbb0a760d', '3bb119b4680e1b0a64f39b8dd6b1b751', '3c2f6a1ba768a1817af6a1b0fd2d6829', '3d26f6d9983a58e48b021d3cffab88c5', '3d5bc3937db9cddea3ed194387ccaf02', '3d671b4df3d8926c121b8735bb7eda6e', '3df52958bf4be68566489cf11341c2e5', '3e8942f943c15ed3d13cdfe56e3add7a', '3ec62b0dd1e50c6c78969b6c68d1fbf0', '3f3d5bcb884cd674ab86f31d27f60b26', '3febb4d05c400b989c3fd22260cd9c43', '402dbd6c08a321940fb39f1e2f0fcb12', '4064332f73895ac3e8844e9359476c5d', '409c7f5f81ac5a826fe411369dac05ee', '4167e79c6d9b3c667a54b22a649f2621', '42016965e8ee94591ca264d9c40a7fee', '421b3a91c722987d21be7d9e7e60132f', '423bc0d5ccf97d44957541a169d16a01', '425b00518f0a8ea83cef0a679205817b', '4280178ce7c21e57267b9c422f1cf8e7', '42e9920bcbfd1627a4b83698e1784a7f', '42f6b8d747b32e2cb7f88e6aade1211e', '4313e04d1e85dc21e881d323d95f0f8e', '43b6117d56fb4e82aa13b89b0137c930', '43d80acf0b720c1b386964b8be503769', '442d9b5e1c0b2d58d79cb1e7d6591c6e', '44a095bd111455c5fdb514afd9389017', '4504c8d8709be441eb9a3fe9a7968089', '4508b4648c6d8259696b528920763299', '4615b6d6c630023d6600e08b962a30b6', '4747d56586d4f91def53018a0b05278d', '477c7c1d25335aed3da4b84cfdd080b4', '47904d5adc26fada4f22219614379c40', '47e7a446438cd936eaf45d954d6834d2', '47f7cc233474923a6c1617228cd23f2d', '4815e974d97015f33408bdf66e9f977c', '48c4a1a16a7ec58cf82cefe60782680d', '491d9c64245990ccbce93ba87482de9b', '496b5d2def73cade181ce757f4233618', '499edefa5d8f42ba3a8729a59fcedddb', '49d03e41ae9a98bd458ff82fafebb715', '4a0c2c4a39fe35ebb164fc08f8d53607', '4a2b76e08f2cb4e2ee27d8c7bfd0c149', '4a6e88d4322d2944aea67e63a6c97150', '4ad506b237573dfdb3a5a4ce581fc55a', '4ad569d8d891f6f982fafbf6d0e06f83', '4b2f8326629c9acb88713e4f1c0a6d67', '4b5c52424856982ac485ed9121aa49fe', '4b9da522888e5ed7e1295d1726b51a42', '4bb319216fe623cc62208b719ea02257', '4bff82436069a452f30623fb0c84391b', '4d25e8ece7d8671a7fc7960021484e4f', '4d388b73da8dd44be3f6d6290db20076', '4d98ac2697041ef4355d32671bcd5ffb', '4e3f56064ae755d4bf0e9a6e94188a79', '4e55a923220fb48f62eb3591524ccd1c', '4e744d3254645f50e40f16236e95823e', '4e7c6f0fe95090256938539c2f9b800c', '4ecc0432ea37f7611cdcd0bdf4221cb1', '4ed68f45ab20b25b935c7864ce71ef0e', '4ff05873e4f78dfaaab1592ccdb96262', '4ff501bcfb6a05bbfe732f52c75c83d6', '5015eb7e4c871ecfb6aa0fac7cb8ff56', '510adfe608ad7cf53f002eb983e691ec', '511c962fba6447dcdc91a1e35656cb8f', '5131c45b56aa75553f51d103490cfee7', '51609468998da51e04da43b94ea5ac26', '51f3b8a3c3bb6b63ee8730ce493ce537', '51f581db3a61ca8ccff208edaf2b6e9b', '520415bc9de8ba1c0d1598339cff143f', '52a99f89cb11bf3213773593f382d4b4', '53092a17afa460689ca931f0d459e399', '535fc9169c96976466b53cc18e67fb93', '53b2a22bc0cafbecf5a210f2030569bd', '54c8bd056aa914d717878ec78a3f9616', '552454c70290e65d653564536c47b5b4', '5536d0b6546f849276c0dd7381355827', '55ff114a55aaa2455f8e6e83a9446b5d', '59b478fd6cfaab3e6735b5de495ff052', '5a2a3f74a88ae24f07b2eb949a708242', '5a58fb02dfd86232ccc3fe8058746a5d', '5ac044a660c0b67c8a9f8d6cb6722720', '5b69f2a0dda3f9ed2d43220d22227775', '5c154a79cbcc1e4d0a356a78fc7fe5df', '5c716b804aa434049fb1374da8bf9740', '5ca0e4e7bdd861975132d028372612f9', '5ca77a764dfe0604a4d42ccc4228eca3', '5cdb18e37b59b32bd4d5baeaa49d2783', '5ceea1a93fb9658cd56636663c132f69', '5d98336b0f63ab2b3d0da2b683f98945', '5d9a3558064210b6f112b31d0a087f2b', '5d9f3e7b6abe8a2f812adf14f3ede5cd', '5e3045190adacd05a3e525c3da336902', '5e8ff39c71b99e912609e17a9be2ab79', '5ec401f998f7317f1803fd4d9ca24e15', '5f02cd6b993d86bedde8c5d57067d9c8', '5f6afae06f428ce79a4a6a680d90e8ec', '5f922c41987dc5b9ea8692acb031e6a3', '5fc35d52a61ab4580379708871178296', '600d2c32c47d0285e1df97492ed3bd35', '611f422068661752e0c6e70870fc4a24', '616a3320fe20e51ad126b5af993123ec', '61a1aed3b75d42b194d23dfc19b7b95c', '61c7f98ff880883b1ac131b2e64dde61', '6270a0f0d81c397c6c2d716974f9b023', '63e1cd9cac66cfb91993831a021866f3', '6484edf52abd4f3e3ef8ff1f1879a59e', '64f5b9e5892495049e6281d03f43f0f2', '650316fa4ce26e4afb99dda16e9ed1eb', '65393345cf140d1963d29683972bcb79', '65870f953c28759363703c1598a95163', '658be343c77318620cdc8897291f26ae', '658fd04a75ad6d56b980d4abb1037417', '6599e20a5bba6ffcea3bf4794351f951', '65bca8fdff73322a0fe8d6fa1f33c470', '65f2b90ff21feb8e5606a34acb5d61a1', '660f3681d1b383739890b13de7b3eb70', '6769cea3c1c104de2728ead8759db585', '677ce9224b160df03d46e737709d51f7', '677dd30bcb999d49a0deea75f4088210', '67d3a651fc21a96f2ff2a47b7f2c34cf', '68a708a906f10e4eff76e8163a25aee3', '696ba7fe929493f16d6bdb8e44037bee', '699189e479d3da859dd4e1264171f1be', '699d6e39df9ec1897d897895a1c12d8f', '69abebb907716a58443606c793e20594', '69bb67622a5f861a0fa9fe4b4cd5d9f0', '69d57af230307d0618717a06a5731185', '6a8a59862c53dde8d6d60571e0b8fb90', '6ac0c532f5f26797392c99628992592a', '6ae5f11fa1638ed6bee8d5a176fc51a3', '6b132457d485853ba4ce43af451dd7e2', '6b9a15b6d16fc70b249049ae75887f91', '6b9e57bb4831313b426330e822bbc6f3', '6ba252ce7a5b578b41aa4750908df855', '6be9846515669aed46b873a1c38f6cc6', '6bfc7ce906ae7cc58610d9fd20571a70', '6c1f559ee05fcd1509a68f1d8172d9f0', '6c4c3d65f69d07ea6ed3ea1fe4b4b9bc', '6c71b07d480a8bd9f0e12b720d01f458', '6d0fc143c0900e22493121708f358096', '6daa544f0704f208645850c20fc00187', '6e780fc35d45a1feff8e08f0943cad74', '6ed2c9f786102e78c6c4eab01d45d72c', '6ed9a4d06f162e7ffc21962eac316efd', '6f0f2168880d84b6457c7c8a4fdc7517', '6f9b768a24c5fd462c34bbc13acc52b6', '6fb4fd6ef7b662eb361720fb0ea1a6b3', '70291a3355b1da2ab0ef4843b97f9596', '70eb79cb99e54debd8ce638d4cb6d46c', '714d6d0586f9e42b81d6c91afbaac0b3', '7198e34461959a4e0684b09ed5429c37', '71e09c51cad39586f539b6d42a5ad7a8', '72190c1d67cfd42c9bbc6e040e7499bc', '7285db5cd39c6b816c18838672d12e0e', '72904221fbda112bda98418ee6fae4f6', '736305451fcfe35768460017e8297577', '7363a3bc1f1b97b8e7b61c9f0cc5972c', '736f126e866c601560e78f2e8b5b4018', '74786eb2e631dcdba7ddc3bdb1211ce8', '74e4dfd116b92012c5d0b43fc6d1c6ce', '7596bbcc409b0c6d462f9ae0fda5bb69', '75b0451ea9f84fb867480808e9da3dce', '75ccd73b458c9d89f2ef775ae41d2925', '7610502e75c13e568ea4dd92e9c85ab0', '7644dc2a0d95d377c6f0737fc889752c', '76b5d2b6557f8d6f69f71691b0c93a67', '76fc457bab4f355a40d5644ee48c1fba', '76fc4dc3ccb87bd46581e1965780e5a6', '772391ccffd7a35bd929a151bb37bf81', '780f59829a6041484daf0827a8420472', '7844c6102c8e771fe495db3a1c7843aa', '789f09767cc8229966798bdf09a002f2', '78d214c6a540fff04b67b209f49dab7b', '78e5a48de602ec6fd6e63a137033e6b1', '796193779e3199e042fa617d89d96145', '79675b90ad62616ee8d7f1ad932145d6', '79eb8474c6ef34c6b30be55d07446bf5', '79ee3662a5c4187045a6e3ce87322e25', '7adf2af0845367d2216fc632a9cb68c0', '7ae3c17d8fb94b354cdc21dc4d42bdf1', '7b0942701728c1eadeb7f565c5a860a0', '7b1054feebf07d36e4b7e700e431a888', '7b1ccd7b050035474f163b6b66e7df53', '7bb22fe6196ffec51d3dbcfb4b958a11', '7c31b22d5e708be58d4c8f0a96502e83', '7c4d8be63fd2c58941f631ad957c0341', '7c6c687200eb0efd89a30fa019f60d47', '7c70a75c3f56290c8b2ee000b6c7a782', '7c9458d95222e7d73f6c1e5a006c584d', '7cb7040c399d173b57ddc23d8f754f7e', '7d1870ba6c0169b57a6c126c986a190d', '7eed51d1873a6f76e3b356eb7711cce6', '7f1df4414a9771c27de4986038a81025', '7fa589e5f88cb61d471bb243f5b39615', '817655ca345b057917b31cef0fe1452b', '81bc6ece0ea4aefefbad7d0959b5cf2e', '822ae50d5e678c8f43bd3f9e574d059e', '8262178fe2087c30ac3b9f7ef890dbcd', '82699e6c92b2cf91122b1051f58174e9', '827ba4e07114d18989b1e1c96c1e5a49', '82eaa9a93a52f743a2bc6d66f9e2b6c0', '83f91cbb9712fc8b29f4075b670b3690', '8405d6a0d0617ec966078df066610e31', '841078183a28463c98d81aebabc938b9', '843172b7434948f024ebead257410e68', '849723360a49846c904a155a68aea528', '84d9841e8c4b53776d4a1f33e9d6da6a', '853e018952b31ade63b6938d321f6726', '85521091a67cefde403d6da2dd8765b8', '855542444d7c48d9000a7aa03dbd8b5c', '87e912b104a2fe7de3f5267b09d7819c', '883d4175c6dc61ffa53184254cf15743', '88d53f1092930e92cd4bde15fea92dc3', '88f07041afea9165aec6213c2e480712', '89383d4f744cb6054b2d3a030ce84b0d', '893a26f6b908f20879e1a57dd738d84e', '893bf9655b68bc80ad3705683663de7f', '8ab9fb61640c2dd13fc2156b8325335a', '8b13e2594dcc9790e518e72428e4e21e', '8b57d4f002b51d958a399c872ffa9776', '8b82e52b995a75fd9448c8c190d08654', '8bd65707c7a3e94cc125d608fff50793', '8c48ff1cc97ac4cdde8572f15a4cd93d', '8c84de06ddc701fbaed2cfe1a09f10c9', '8cb7a61df5c9345ce27d484411cb5d82', '8d6d9c1e8a75bb578327a79661dd51ae', '8d8094576836a1b15267cf132f76d1b0', '8e0d5135f716204b39a88fb9fdebbe2d', '8e524f7c56ef7b948dcf1d5105c6907a', '8ecff412c566d1cc42ee358fcaa6c342', '8f12de9b3ab88f7e5928976cc6aa8568', '8f9f2cb5656a8a14ba89cf094af840bc', '8fa61ec04464c88da7e18b6a776b2edb', '8fbd1899d2cf59104fcb4aaa77d7181f', '8fbfb99643abf25bc3513e19451f0573', '9040008203fdf63593ef50486857dbda', '9053623e69b128d35ba4950cf3954a95', '90b7a22db5e16e1ea05cc088c8e5149f', '915e0b1e99e535d1cf62027431acb0f5', '91b94a946949d56659700bb0b85dbd16', '9238b74653b883e0f3df24c9994914cd', '92d1c417667758777b688bb4abddfa09', '93066dae331c672d925e2100e6e5b2db', '93641092c6bac74871724e498081256f', '94f7a1d025ab987b7a72393bef5b3312', '958115dae60f5d85ec76e6c39227d101', '960ce7886f9068becce050266d67f238', '9680d74f68cd8b8dfe2655389aeb2a92', '96b8bb8d47f34c5d96fbb71033c6b038', '97270b4aeff630f1d8b7511cfd880e2d', '97424181faafce7d36d364936d4f5a53', '977db81e0db3f2d61bf3d8331d3b48d8', '97da7db8ea1c59ec8fb1fb7b87d5cb00', '9847c685e61ae42c37b8903bc1bdb473', '990483e02f5118bbeebb827f93bc6b14', '99103f804200ba86ea70975c951e99cc', '994dabdfe2cabbc8620ab4e87d3d727a', '99779601b07bf7d900a5723dd76941b7', '99ae5a3aa433f67e7613653ba1c6c371', '99ea121a9a9e6ec3558cf193cac080e6', '9a1a4c6641d3923f67dd9446a93dde9b', '9a296eecaf935086c3ff61bec0c0f5c8', '9aafbe04cef21cebaf86f6908839906c', '9b7e6c85198e358f92ed095556771fc5', '9bc891e280c0208b4412c5122a8ec7fb', '9be0dbdf84c92ee27f804e321374c3f1', '9c9e0f1e1419ea97fe9ac6288a301769', '9ca2cb7c1486635b319d6fbc9458d18c', '9cbdff30a9b54764fd40e6b518625623', '9cf053e9dc2bd0359052185017a3386c', '9d2512bf7ce0a6a0cfcb7d4ddad49566', '9d685e75c1e3b62221b2279fb82e9669', '9d9603034996370d2a6c2bf4c70b9de5', '9dc3c1b190b54ff0173dc6966243b18c', '9e128a4147bc9a6b29f0624dee528b13', '9e48923d8daf249805d92e5b2a2effa8', '9e6412291a9eadab52cf9aa768484bca', '9ec2ce4ac12c207e41ce2d150b0772a3', '9f9fbf0bce6f4eb4d476a74fca5b34d5', 'a04b28de89948e1e21a12968faa9865e', 'a0706dc489b61cc59cadf217ab3cc02f', 'a0c74630c0cad897ef16809480082cf5', 'a0ebac2b0f37f2aebb8e736042ce9afc', 'a0fa15835ecca4c6fc670e10939c9ead', 'a17b03734af47f9e2c53d612a9862db2', 'a2d8c9c1a2f8b91a9a733f8ac4799b27', 'a3530ef51de742597955b394f811a7b7', 'a38282a55c24de868309ab5eab674de1', 'a3acc4f8510ac989967b2e9c595b19bb', 'a3cf02a00d86beba7e83a89be2dccc4b', 'a3d3f1977e60f3975a62681f116c24d1', 'a4477ab6b9b041360c90e87a95243d32', 'a454caa167464535459a19b0f967fc3a', 'a470e44eb3ad3022dc8d19790c5c236b', 'a4bf73a647ab00f37e9f852444cb5374', 'a4c0021f0146f40f36c31bb71b21d512', 'a4d8a73d91e7749674aefc37a356bd55', 'a5606339c22f0bee1dca9f8d42730d32', 'a56c9bc9c7b48d5c9ac66366c22c4000', 'a5aff186cf4ccd70107c1cbb732e2571', 'a618e7a295e8fcc9910612956163514a', 'a62954022e59254ec0a8bace79e79d91', 'a7109bcb92fe1455e20b8bc60569f8dd', 'a71e917377f86b0fca949f1fde2b8845', 'a7834e3658ad6f205e8c3edfe7eb2060', 'a7a6b5c0ac5cbbcabb054711155ceb09', 'a7ab73ae5af0b58d92bed61aae54d74c', 'a7bf06290200454d84c96bd61aa1da1c', 'a8429b306433c214d5108804e5a454ab', 'a857b441391a271d2a07cea50acc9e23', 'a8bb03ecaf8b54f437ffdfab72bb1357', 'a8dd469e0efe9ba6555e3600ffa09e2a', 'a96450f56000c4f0184f6c4090a731a7', 'a9f112e5eb2b08896c89032231bb6689', 'aa387185e6f85b9428a753221110c877', 'aa395b2c3a052f5f6d4943c976517fb4', 'ac0bb74dd418f6d3f316eccc993f8831', 'ac1c6a857698c13d4397ed97a20bb5f6', 'acce1e38286b207aa3c9095b4c4a6f33', 'adad7b75f894ccba9bff546cf18c0aa4', 'adf94eb8bd0cef2fba0d648e0a78f4cc', 'ae4a9a64c8400ab7d561f59a99a8db3a', 'ae75ed51bd14bf2ad770e440b070d6af', 'ae920eb1894a3cdf00868ded5f25f4a6', 'aec0519588ac10be535a9fe0645dc264', 'afad18e4420794c9e1b916da2e68e154', 'afaf847c46818478ae119d477617685b', 'afdcf3ea1a709e78ea2942f4bcef11ac', 'b0589fa585cd0747e00b7bba56a85a58', 'b198c791d91d5d0392d17ed411728187', 'b1efe19c0bc38ef7a48faf1817dce45d', 'b229b12e51907f9326b60d8bdeb582ec', 'b23322eb31970d65b480e3f45d3d3e4c', 'b266170835ff0626da0d2c8d245a4da1', 'b3df337f8ec11540352b5c8b02f7accd', 'b41f47ccf643f662e8a6a4d19aa82961', 'b44d8535beb9f13f0468ad0ac255da70', 'b4f51716687ff279a2e56e6920744bec', 'b5464d2f0c37290ee82288a6e1b25c48', 'b56a9cd89da52d92278365938939fb7f', 'b5a7331c87350e99c1bd061992ac04f7', 'b62981bada4c26c9fc2eda9765a0d9b6', 'b63258be7c817e40e7008a04944324fa', 'b65cc533f6ef4b6b5ac8f02565de959f', 'b66a03904411f8aa55a90112a050573b', 'b69432e9e3903785426439a2c24fac5b', 'b6df81d99e3f863846e98ee8f9f65022', 'b7097bd2d8c16574e4f95564e399ecfd', 'b72a217882694ba02046e89f50640682', 'b8801cc8d450e9fb2f5af098854181ef', 'b93c001218949705bf42ce42920c79f3', 'b99b68b557d7980e48bfb760616dabe4', 'ba5a14288e851811820f8ef25ac040ac', 'baa8bc418b0c160a5c0d21d68a47f66a', 'baf63cb2fa9284ac9407bfd08383313d', 'bbbd2bffc4ab3145b6599d87f04017b2', 'bc7e7ce016865b88cc1b1932ab649ec8', 'bc84e1c8f1af6ca9b1516264fbb2568f', 'bcb13183f00f06073f4e07f73741e5d3', 'bcf7776e069f56bd56cddb6cb29d7580', 'bcf9197e9b9757e2691faf529fd90a12', 'bdb0c593de18dd2991a6d69d27c20e59', 'beeacd933b2def26105ee2dadeb42f66', 'bef09ccd7d5c8b261dd336e5a7472a7f', 'bf01950262c3cd0d14b618840cf64ec4', 'bf4f1084d793b1cf459106c4d958b45b', 'bfa53e507fc3c65661f470e577fb6ada', 'bfec41a7c069a33ce3228b5e4b096ccb', 'bff8d59e1b91b650858aeae2ac6f3aba', 'c025ae9f3e8caf615eff902386cb72d7', 'c02c89d9649d11515c469785bca5199d', 'c06dcc0df07750f95a0d5b2662805db3', 'c0f939bc03284dda39e710cd5369ed3b', 'c1038066fcf0b4f7040e74e2977187b1', 'c11ed90bb4e61dd40b85f6c5a93437dd', 'c154073984eab4a9faaeaad9f0444866', 'c18dfe92cb10705d980fc87ac302cfe0', 'c1b23507a6385e1492d1c9402a6aa98e', 'c379f44cee35e3d495b662882cd14879', 'c3f10249250e4edba80134a5def65f09', 'c4122cbbb0945c6d43527199c3b37af9', 'c4882d7cdf05b6aa5b462472b62a580d', 'c4916040bd79032418922ad4b4481c93', 'c4dd7cdb509885c10398e6e137c62c2b', 'c4f5941ac8a41ca2efd8de31effcde24', 'c5257970de3b109e51613621fb265af7', 'c552ef320b48da156ad6f2c118e45197', 'c553024a325f5bcd2216c7fdf25e7e21', 'c589ce7c88977b4f1629c60e79a485a6', 'c669c44329555e2fb76bde8b7fad28d9', 'c6e7dd8179aea3e68959a26d563c24a8', 'c78b7a1ab85a26ac46f66459bee178e6', 'c863b48c06a88e6462e2538f5e1adca5', 'c8ae3b5763acac926c24f8fdbbd7d35d', 'c981ac5f7c3d73a6b467dc9abfb601af', 'c9dcaa9ec6e4881b9b7b89d68bd1b978', 'ca0102a8a6e6baa9c8297febd67bddb8', 'cb11c938626232cdd8c5eb321f1f469d', 'cb138a335bbcfc764be35e3a3255fb64', 'cc1749d4cd5722d7ad06f29a2983effb', 'cc20a8db0e0cb6e810925e189b86c93f', 'cc355496166de5d9b03af70a18e3e80a', 'cc717be975df865603c419ee8b132772', 'cc8d86b35d9728d187dc7ab913538d98', 'ccde8e8961e69a74d8273d1734efdce7', 'cd9751214b3ec0997dc2d113e1666192', 'cdcf41d6fd5475016a10378f6fff81a7', 'ced98523c4069ea8f4791a7ac92da225', 'cefc39f66901063fcac373cb4ea4e923', 'cf5989a5bdb31888bdec793498a7736a', 'cf73f5fc3119f96b554927cd80868609', 'cfc8e1c2517bd58195767e1ef1c27ac3', 'd017974fa33967cff994280ac36be613', 'd12561ced5b6f5e75eaa69b65df0c5c1', 'd16090208b61dab7abb792d65661d9b0', 'd16327ed92654064aae2731edf2f1d77', 'd31c7dd8393ed89bd087f9e3ec10dc98', 'd33b0cccdc0ca5b5678f621f0080f538', 'd4f57b02200ddb0178a118dbc7b01764', 'd5c08247cf6242888dee937ffbb229a8', 'd659002d75c902ac708be7170c0f1cd9', 'd66e03798417c45337a87e7c8252316e', 'd6d77587b29d31a522302d6b967bdf03', 'd6e895299094a96518baf3317ea1d679', 'd6f62ba861bbf933dfea4fc5689e1714', 'd75a7f10671a7fa8e02a0089a0b03687', 'd7de44fd6404c87148f53e473c04467b', 'd83dfb5f7066831350ce29fa78f68b55', 'd86b364a56a29b649b082ed76518e227', 'd95bdd29c9c0ab7fb136745f6d6813c4', 'd9850b72111914c7fe899a3a64c1234a', 'd98db923c5ced02a40820e7a9aae1385', 'd9a4d82001debc9094d893722ce3d5d7', 'd9bdfdeefc235f4c7ca55cd23a62b435', 'd9bfb1be75800d3137b1ac2b987630e3', 'd9ca2779ccad800875db756eb758718f', 'da0bdcc9ba954acc879dd0b6ab96065c', 'dac31a015ca5f268dc134da6cb4eba07', 'dacf9167919597fb59e4fd1b583bcf16', 'db779dcf8bacbf65b295b527e8d92e9d', 'dbfdec22f60b3b3dbb97d8bc7c8c459c', 'dd232a202f98c3d367c4475a65fcefce', 'dd6b1b64f0c2471f275b2f20e9054ef9', 'dda03f3ce0969300902c288ce9d16099', 'de12dbe51a827faaac8cbdf04f539c01', 'de7690f001f414ef10c061b7bd484458', 'df244a7df84e522128c448472cc3db21', 'df354d595fa70b1732a25aa272594171', 'df64f6ced72480613a23a8a8f7c17f17', 'dfa99951bdbae430461dac85e915391d', 'e06c083a639fb851333aa5c79331c848', 'e10992dbaac1aafcffbc0d39688feba1', 'e1bd7a5a6b11d0d3db87919d79d26303', 'e1de0834b626a6db646936e0747637d8', 'e2a01e463b70dff0e2c3b81a3c14abd6', 'e37134fe03d1356dec3d4862a95d3124', 'e4005aa9fecf636872724209b03d1de4', 'e46999b9786be7cd86ec59b6de3b2e67', 'e4a70ce747207af1112c14120183de6d', 'e4dadea0a1a75c3788d92f4dac3fdb4d', 'e5c747a08ed2544a30f863a01ddb2705', 'e5e503bb14f3aa94af8b436ccda2abaf', 'e6e2748f545e8c1c2696aedb3cede96e', 'e75f247b57b240d9a3cce8ca3515b40f', 'e768d96e8d8384ff3d7f2ec16ca5a1a2', 'e7718165070e55cc57a6c07e9089a65b', 'e789c7156d559cf383c5454e1fe72c48', 'e7e19bee8d483cf60dc209e75972653a', 'e7e48cd1dffb189fffa55620881f060f', 'e7fccda8437cfae91931555e2f3fa13f', 'e870b154d79ffd5242603e0d4839e3fa', 'e88aa4796a5b50bf70ce34694c68aa2b', 'e8e3d6a0e5433fd929aebda823a02d9e', 'e90e478e3f295acb360bf895344c0148', 'e9117524cb0709d58952e82facba7711', 'e9486b4acefd3ab7b735a4695607cded', 'e9e9be1eb9c214455016d845f668e7d4', 'ea209f48b81c3e55ad656a479118560c', 'ea2bfdcf00fae7663c49a859aad7f555', 'eac85f1f52ddf309e6f53f0cd13c5d52', 'eb9d3964ed90bc0b75776fa27164779c', 'ebe4fbc7d47b006e649747f6ea53fa43', 'ec0539c98fcb0809cfd47f3ec80d0822', 'ec68a8f82b620ca9fdab9d3b637dae5d', 'ec752bef365ad2394e56ee664521d766', 'ec92c9624af3e561b1c3fdacd5176e94', 'ed0a12e2bb136b08380dae9cadc103f7', 'ed206e6022adde76c856f4e8bf95e3a7', 'ed68e8dc5c670ac07f1be6d425c63749', 'ee0bcd8823e24b48772524b4108252d0', 'ee401c45f2bb7495b0e7f0c5eee1f2ec', 'ee631763bc437869ac84d604bb87cc60', 'ee8390c1b1f9373ad91586213529bd70', 'eecc5686192efb8f552148a46ca36df5', 'eed4ec941bd7279fd94a413950b7acd0', 'ef1630a5ff40cce0c45e07b7b0e2ff3d', 'ef269d45c622c3599367e50d214d7f0f', 'f0270a0e16a8b0b026696a28eb4f005e', 'f030e04a4bd5aa2d79ebd6037ab3e8a4', 'f0aa97d5238b428b193c4367ca36b992', 'f1c66b732f63c8ffc90520b1c08d049d', 'f1ec61940c9a9192a84f846b81845606', 'f2418dfbb040bacf4201a2a7db861953', 'f2ada6c73cfea539bfc9db0abc60127c', 'f2fd52ea7cd10abe5b5bf18ec113e6b9', 'f4972fc643d315bc32a1b6e5164c0ac9', 'f4c97e252215857151862e5c64d1cde9', 'f4dd2a38ec7ce06686a930bc9743c9df', 'f58680e802368ca8e3b78335a87342a8', 'f5a7c3e251db356f4117effa6e9ea901', 'f5d1ccb5fae8ad747a7b166a6999b9c4', 'f5d5fb5ae1ed2aae5ed68a78f93c8ed1', 'f5f4a70818e4a3151d69f6c7224788d0', 'f679c5442179677b17cdd25dc1e143fd', 'f69a837170aa19c4bf455bda9d3a6d23', 'f6bdc0d16fa4d142d8c8b6fdb4f5e5dd', 'f778323f27d59fec2716f506fbfa394f', 'f7b9f4d3813b108b74b710872a6ee0e2', 'f7f7f8a4d2fd3506705f5b54bd44894e', 'f815070cc52ceeee6e11879ec6e173fe', 'f84a078a4cd5ffe9708c0e674ec69039', 'f87c5bfda7345be9c051264f48b8a3d3', 'f8b27a4f72bf8fe6b4d8348cb85f8739', 'f8fd1bb4d9d99e504b6863cabe62cee4', 'f90e0c86367f9e0b0484746a404f077f', 'f92450ee1639205d548fe5936cfbcc5b', 'f964bdd1c3c54ca739e86d3a755a0fc2', 'f97706f0acd05d36c9363ff98b911661', 'f985cefd833f54f8a9db364ece99faa0', 'fa01862cfaf8f5cbcb089c63f5368892', 'fa37811f94fe322f46962969c38f61b2', 'fa9a044c8c85e53ba24ae97a78ccda1c', 'fad96276f9ffdd8b1ed8ff186da526d2', 'fb57a7f867ee8be22dc9da2f35b449ea', 'fb6186ae8931c2cb380cbeddcbbc0f26', 'fba3b601dca474b8bd3ca5158464f5b9', 'fbc85ebaac52dad1f19514782d13db5e', 'fbc8c05c4af9bfaaadba8b230a876eea', 'fbcd31a8ab10f51673db458d9d472e9f', 'fc8963092bf546fa6a5cdd14a3161fec', 'fcb7d58842017b2833d8550c276dc352', 'fd4902c24a8f630d82cc2e9b997a0a01', 'fda25dcfd9ccc655bd9bf18177c48f52', 'fda78d37f8b6f19875d7eeaf15620f76', 'fe28d89d329a256c66e20ce7c84ee9f7', 'fe3f80ed51105726d6ce8774916728ab', 'fe50f24ce2407562824c1c89779ee36b', 'febefc5c5361c1e72c87755806f01f2b', 'fee3c7cb6fa0bdfa428b3546b8190c89', 'ff0793ceab8e9a4936b06c7a097a91fa', 'ff137c9da5069502d47c75c84647c7ca', 'ff32c9a32957a8702923282395ac2128', 'ff5026a8ca2370fc56f26683f82b683a', 'ff554d962af00e293537f4348fee5d06', 'ffa684d9b2e9741c20deddc6f0769a25', 'ffd302f909de701f0c8ea79d2a974efc', 'fffb3376fb6b5fe80a3d48a854094773']
                if assigneeID not in unresolvable_assignees:
                    self.assigneeDict[assigneeID]["officialType"] = assigneeType
                    self.assigneeDict[assigneeID]["private"] = isPrivate
                else:
                    self.assigneeDict[assigneeID] = {"urban": None, "country": None, "state": None, "latitude": np.nan, "longitude": np.nan} 
                    self.assigneeDict[assigneeID]["officialType"] = assigneeType
                    self.assigneeDict[assigneeID]["private"] = isPrivate
                #print(assigneeDict[assigneeID])

    def parse_patent_assignee_correspondence(self, sourcefile="patent_assignee.tsv"):
        """Method to parse patent-assignee correspondence. Populates patent dict with 
           corresponding assignee data."""
        count = 0
        with open(sourcefile, "r") as ifile:
            _ = ifile.readline()
            for line in ifile:
                count += 1
                print(count, end="\r")
                elementi = line.split("\t")
                patentID, assigneeID = elementi[0], elementi[1].replace("\n", "")
                
                # match 
                locRecord = self.assigneeDict[assigneeID]
                self.patentDict[patentID] = {"urban": locRecord["urban"], "country": locRecord["country"], 
                                        "state": locRecord["state"], "officialtype": locRecord["officialType"],
                                        "private": locRecord["private"], "latitude": locRecord["latitude"], 
                                        "longitude": locRecord["longitude"]}
                #print(patentDict[patentID])


    def populate_and_save(self, end_in_pdb_shell=True):
        """Method to govern population of the records from source files.
           Will transform patentDict to pandas and save the data frame in the end.
           No Arguments, no returns."""
        if not self.locationsDict:
            print("Parse location data ...")
            self.parse_locations()
            self.tempsave()
            print(" Finished.")
        
        if not self.assigneeDict:
            print("Parse assignee data, match location data...")
            self.parse_location_assignee_correspondence()
            self.tempsave()
            print(" Finished.")
                
        if "officialType" not in self.assigneeDict[next(iter(self.assigneeDict))]:
            print("Parse assignee type data...")
            self.parse_assignee()
            self.tempsave()
            print(" Finished.")
                
        if not self.patentDict:
            print("Parse patent data, match assignee data...")
            self.parse_patent_assignee_correspondence()
            self.tempsave()
            print(" Finished.")
        
        print("Transform to pandas and save...")
        self.df = pd.DataFrame.from_dict(self.patentDict, orient="index")
        self.df.to_pickle(self.table_save_name)
        print(" Finished.")
        
        """Allow manual inspection before script terminates"""
        if end_in_pdb_shell:
            print("\nAnything else?")
            pdb.set_trace()


# main entry point

if __name__ == "__main__":
    
    ADP = AssigneeDataParser()
    ADP.populate_and_save()

