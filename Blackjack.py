#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from logging import shutdown
import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, OneShotBehaviour, PeriodicBehaviour, TimeoutBehaviour, CyclicBehaviour
from spade.template import Template
import itertools
import random
import sys


class Dealer(Agent):
    podijeljeneKarteIgraca=0
    class PodijeliKartuDealeru(PeriodicBehaviour):
        async def run(self):
            karta = random.choice(moguceKarte)
            if(total(sadrzajRukeDealera)<17):
                msg = spade.message.Message(
                    to="aoletic_prvi@rec.foi.hr",
                    body=karta,
                    metadata={
                        "ontology": "podijeliDealeru",
                        "language": "hrvatski",
                        "performative": "inform"})
                await self.send(msg)
                print(f"Dealer je izvukao: {karta}")

    class PodijeliKartuIgracu(PeriodicBehaviour):
        async def run(self):
            if(Dealer.podijeljeneKarteIgraca<=1):
                Dealer.podijeljeneKarteIgraca+=1
                karta = random.choice(moguceKarte)
                msg = spade.message.Message(
                    to="aoletic_prvi@rec.foi.hr",
                    body=karta,
                    metadata={
                        "ontology": "podijeliIgracu",
                        "language": "hrvatski",
                        "performative": "inform"})
                await self.send(msg)
                print(f"Za igraca je izvuceno: {karta}")

    async def setup(self):
        print("Dealer se pokrece!")
        print(f"Ovo su moguce karte u deku:{moguceKarte}")
        print(f"Ovo su moguce akcije:{moguceAkcije}")

        start_at = datetime.datetime.now() + datetime.timedelta(seconds=3)

        podijeliKartuIgracu=self.PodijeliKartuIgracu(period=5, start_at=start_at)
        self.add_behaviour(podijeliKartuIgracu)

        podijeliKartuDealeru=self.PodijeliKartuDealeru(period=5, start_at=start_at)
        self.add_behaviour(podijeliKartuDealeru)

class HitAgent(Agent):
    class PodijeliKartuIgracu(OneShotBehaviour):
        async def run(self):
                karta = random.choice(moguceKarte)
                msg = spade.message.Message(
                    to="aoletic_prvi@rec.foi.hr",
                    body=karta,
                    metadata={
                        "ontology": "podijeliIgracu",
                        "language": "hrvatski",
                        "performative": "inform"})
                await self.send(msg)
                print(f"Za igraca je izvuceno: {karta}")

    async def setup(self):
        print("Igrac je odabrao hit te je podijeljena nova karta igracu!")
        hitAgent = self.PodijeliKartuIgracu()
        self.add_behaviour(hitAgent)

class Player(Agent):
    class UcitajPodijeljenuKartuDealeru(PeriodicBehaviour):
        async def run(self):
            msg = await self.receive()
            if msg:
                sadrzajRukeDealera.append(msg.body)
    
    class UcitajPodijeljenuKartuIgracu(PeriodicBehaviour):
        async def run(self):
            msg = await self.receive()
            if msg:
                sadrzajRukeIgraca.append(msg.body)
            if (len(sadrzajRukeIgraca)==2) and total(sadrzajRukeDealera)>=17:
                akcija=odluciAkciju(sadrzajRukeDealera, sadrzajRukeIgraca)
                if(akcija=="Hit"):
                    await hitAgent.start()
                else:
                    score(sadrzajRukeDealera, sadrzajRukeIgraca)
                    quit()
            if (len(sadrzajRukeIgraca)==3) and total(sadrzajRukeDealera)>=17:
                score(sadrzajRukeDealera, sadrzajRukeIgraca)
                quit()

    async def setup(self):
        podijeliDealeruTemplate = spade.template.Template(
            metadata={
                "ontology": "podijeliDealeru"})
        podijeliDealeru = self.UcitajPodijeljenuKartuDealeru(period=5)
        self.add_behaviour(podijeliDealeru, podijeliDealeruTemplate)

        podijeliIgracuTemplate = spade.template.Template(
            metadata={
                "ontology": "podijeliIgracu"})
        podijeliIgracu = self.UcitajPodijeljenuKartuIgracu(period=5)
        self.add_behaviour(podijeliIgracu, podijeliIgracuTemplate)

def odluciAkciju(sadrzajRukeDealera, sadrzajRukeIgraca):
    akcija=""
    if total(sadrzajRukeIgraca)<=11:
        akcija="Hit"
        print(f"Igrac uzima u obzir svoju ruku te {sadrzajRukeDealera[0]} od Dealera")
        print("Igrac je odlucio akciju Hit!\n")
    if total(sadrzajRukeIgraca)==12:
        if "Two" in sadrzajRukeDealera[0] or "Three" in sadrzajRukeDealera[0]:
            akcija="Hit"
            print(f"Igrac uzima u obzir svoju ruku te {sadrzajRukeDealera[0]} od Dealera")
            print("Igrac je odlucio akciju Hit!\n")
        if "Four" in sadrzajRukeDealera[0] or "Five" in sadrzajRukeDealera[0] or "Six" in sadrzajRukeDealera[0]:
            akcija="Stand"
            print(f"Igrac uzima u obzir svoju ruku te {sadrzajRukeDealera[0]} od Dealera")
            print("Igrac je odlucio akciju Stand!\n")
        if "Seven" in sadrzajRukeDealera[0]or "Eight" in sadrzajRukeDealera[0]or "Nine" in sadrzajRukeDealera[0]or "Ten" in sadrzajRukeDealera[0]or "Ace" in sadrzajRukeDealera[0]:
            akcija="Hit"
            print(f"Igrac uzima u obzir svoju ruku te {sadrzajRukeDealera[0]} od Dealera")
            print("Igrac je odlucio akciju Hit!\n")
    if total(sadrzajRukeIgraca)==13 or total(sadrzajRukeIgraca)==14 or total(sadrzajRukeIgraca)==15 or total(sadrzajRukeIgraca)==16:
        if "Two" in sadrzajRukeDealera[0] or "Three" in sadrzajRukeDealera[0]or "Four" in sadrzajRukeDealera[0] or "Five" in sadrzajRukeDealera[0] or "Six" in sadrzajRukeDealera[0]:
            akcija="Stand"
            print(f"Igrac uzima u obzir svoju ruku te {sadrzajRukeDealera[0]} od Dealera")
            print("Igrac je odlucio akciju Stand!\n")
        if "Seven" in sadrzajRukeDealera[0]or "Eight" in sadrzajRukeDealera[0]or "Nine" in sadrzajRukeDealera[0]or "Ten" in sadrzajRukeDealera[0]or "Queen" in sadrzajRukeDealera[0]or "Ace" in sadrzajRukeDealera[0] or "King" in sadrzajRukeDealera[0] or "Jack" in sadrzajRukeDealera[0]:
            akcija="Hit"
            print(f"Igrac uzima u obzir svoju ruku te {sadrzajRukeDealera[0]} od Dealera")
            print("Igrac je odlucio akciju Hit!\n")
    if total(sadrzajRukeIgraca)>=17:
        akcija="Stand"
        print(f"Igrac uzima u obzir svoju ruku te {sadrzajRukeDealera[0]} od Dealera")
        print("Igrac je odlucio akciju Stand!\n")
    return akcija

def total(sadrzajRuke):
    total = 0
    for card in sadrzajRuke:
        if "King" in card or "Queen" in card or "Jack" in card:
            total=total+10
        if "Ace" in card:
            if total>=11:
                total=total+1
            else:
                total=total+11
        if "Two" in card:
            total=total+2
        if "Three" in card:
            total=total+3
        if "Four" in card:
            total=total+4
        if "Five" in card:
            total=total+5
        if "Six" in card:
            total=total+6
        if "Seven" in card:
            total=total+7
        if "Eight" in card:
            total=total+8
        if "Nine" in card:
            total=total+9
        if "Ten" in card:
            total=total+9
    return total

def score(sadrzajRukeDealera, sadrzajRukeIgraca):
	if total(sadrzajRukeIgraca) == 21:
		print ("Čestitamo, imate Blackjack i pobijedili ste!\n")
	elif total(sadrzajRukeDealera) == 21:	
		print ("Nažalost, Dealer ima Blackjack te ste izgubili\n")
	elif total(sadrzajRukeIgraca) > 21:
		print ("Nažalost, imate više od 21 te ste izgubili.\n")
	elif total(sadrzajRukeDealera) > 21:			   
		print ("Čestitamo, Dealer ima više od 21 i pobijedili ste!\n")
	elif total(sadrzajRukeIgraca) < total(sadrzajRukeDealera):
		print("Nažaost, Dealer ima više te ste izgubili.")
	elif total(sadrzajRukeIgraca) > total(sadrzajRukeDealera):			   
		print ("Čestitamo, imate više od Dealera i pobijedili ste!")


        
if __name__ == '__main__':
    global sadrzajRukeDealera
    sadrzajRukeDealera = []

    global sadrzajRukeIgraca
    sadrzajRukeIgraca = []

    global bodoviRukeDealera

    global bodoviRukeIgraca

    global moguceKarte
    moguceKarte=["Ace of clubs", "Two of clubs", "Three of clubs", "Four of clubs", "Five of clubs", "Six of clubs",
    "Seven of clubs", "Eight of clubs", "Nine of clubs", "Ten of clubs", "Jack of clubs", "Queen of clubs", "King of clubs",
    "Ace of diamonds", "Two of diamonds", "Three of diamonds", "Four of diamonds", "Five of diamonds", "Six of diamonds",
    "Seven of diamonds", "Eight of diamonds", "Nine of diamonds", "Ten of diamonds", "Jack of diamonds", "Queen of diamonds", "King of diamonds",
    "Ace of hearts", "Two of hearts", "Three of hearts", "Four of hearts", "Five of hearts", "Six of hearts",
    "Seven of hearts", "Eight of hearts", "Nine of hearts", "Ten of hearts", "Jack of hearts", "Queen of hearts", "King of hearts",
    "Ace of spades", "Two of spades", "Three of spades", "Four of spades", "Five of spades", "Six of spades",
    "Seven of spades", "Eight of spades", "Nine of spades", "Ten of spades", "Jack of spades", "Queen of spades", "King of spades"]
    
    global moguceAkcije
    moguceAkcije=["Stand", "Hit"]

    player=Player("aoletic_prvi@rec.foi.hr", "badel1862")
    player.start()
    hitAgent=HitAgent("agent@rec.foi.hr", "tajna")

    dealer=Dealer("aoletic_drugi@rec.foi.hr", "badel1862")
    dealer.start()

    input("Pritisnite ENTER za gasenje programa!")
    dealer.stop()
    player.stop()

