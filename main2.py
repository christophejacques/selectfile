import pygame

from typing import Callable, Union
from functools import partial

couleurs: tuple[str, ...] = ("bleu", "blanc", "rouge", "vert")


class Variable:
    Running = True
    Menu: str = ""
    Bleu: bool = True
    Blanc: bool = True
    Rouge: bool = True
    Vert: bool = True
    taille: dict = {color: 1 for color in couleurs}


class Mouse:
    pos_x: int = 0
    pos_y: int = 0

    @classmethod
    def set_pos(self, x_or_coord: Union[int, tuple, list], y: int | None = None) -> None:
        if isinstance(x_or_coord, int) and y is not None:
            Mouse.pos_x = x_or_coord
            Mouse.pos_y = y

        elif type(x_or_coord) in [tuple, list]:
            Mouse.pos_x, Mouse.pos_y = x_or_coord  # type: ignore[misc]

    @classmethod
    def get_pos(self) -> tuple[int, int]:
        return Mouse.pos_x, Mouse.pos_y

    @classmethod
    def get_diff(self, x_or_coord, y: int | None = None) -> tuple[int, int]:
        if isinstance(x_or_coord, int) and y is not None:
            return Mouse.pos_x - x_or_coord, Mouse.pos_y - y

        if type(x_or_coord) in [tuple, list]:
            return Mouse.pos_x - x_or_coord[0], Mouse.pos_y - x_or_coord[1]

        raise Exception("Le type des parametres n'est pas correct.")


def fprint(*args, **kwargs):
    print(*args, **kwargs, flush=True)


class SubMenu:
    parent: object
    sub_menu: object
    opened_sub_menu: object

    pos_init: tuple

    draw: Callable
    is_open: Callable


class Action:
    index: int
    libelle: str
    raccourci: str
    etat: str
    fonction: Callable | None
    sub_menu: SubMenu | None = None

    def __init__(self, 
            libelle: str,
            raccourci: str,
            etat: str,
            fonction_or_submenu=None,
            *args, 
            **kwargs):

        self.libelle = libelle
        self.raccourci = raccourci
        self.etat = etat.lower()
        match raccourci.strip():
            case ">":
                self.fonction = None
                self.sub_menu = fonction_or_submenu
                return

        if args:
            part1 = partial(fonction_or_submenu, *args)
        else:
            part1 = fonction_or_submenu

        if kwargs:
            self.fonction = partial(part1, **kwargs)
        else:
            self.fonction = part1

    def __str__(self):
        return f"{self.libelle!r} {self.raccourci!r} {self.etat}"

    def set_index(self, index: int):
        self.index = index

    def set_sub_menu_parent(self, parent):
        self.sub_menu.parent = parent

    def is_sub_menu(self) -> bool:
        return self.raccourci == ">"

    def exec(self):
        if self.fonction:
            self.fonction(*self.args, **self.kwargs)


class Menu(SubMenu):
    titre: str
    liste_actions: list[Action]

    screen: pygame.Surface
    surf: pygame.Surface 
    surfo1: pygame.Surface 
    surfo2: pygame.Surface
    selecta: pygame.Surface
    selecti: pygame.Surface

    font24: pygame.font.Font
    fontsymbole: pygame.font.Font
    pos_init: tuple[int, int] = (0, 0)

    show: bool = False
    animation: bool = False

    parent: SubMenu | None = None
    opened_sub_menu: SubMenu | None

    index: int = -1
    selected_index: int = -1
    old_index: int = -1

    alpha: int = 0
    goutiere_size: int = 30
    border_size: int = 2
    select_size: int = 22
    taille_ombre: int = 3
    height: int = 0
    min_width: int = 180
    width: int

    @classmethod
    def init(self, screen: pygame.Surface):
        fprint("Menu.init")
        self.screen = screen
        self.font24 = pygame.font.SysFont("segoeuisemilight", 12)
        self.fontsymbole = pygame.font.SysFont("segoeui-symbol", 12)

    def __init__(self, titre: str = ""):
        self.titre = titre
        self.time_for_action = 0
        self.opened_sub_menu = None
        self.clear()

    def clear(self) -> None:
        self.width = self.min_width
        self.liste_actions = []

    def add(self, action: Action) -> None:
        action.set_index(len(self.liste_actions))

        lib = self.font24.render(f"{action.libelle}", True, (0, 0, 0))
        rac = self.font24.render(f"{action.raccourci}", True, (0, 0, 0))
        width_lib, height = lib.get_size()
        width_rac, height = rac.get_size()

        new_width: int
        if action.raccourci:
            new_width = 6+3*self.goutiere_size + self.border_size + 10 + width_lib + width_rac 
            # if action.raccourci == ">":
            if action.is_sub_menu():
                action.set_sub_menu_parent(self)
        else:
            new_width = 6+self.goutiere_size + self.border_size + 10 + width_lib + 16
        if new_width > self.width:
            self.width = new_width

        self.liste_actions.append(action)

    def compute(self):
        # doit etre execute apres clear() et add()
        # fprint("Menu.compute")
        self.height = (2 * self.border_size + 
            self.get_nb_separateurs() * (1 + 2 * self.border_size) +
            self.get_nb_actions() * self.select_size)

        # surface du menu
        self.surf = pygame.Surface((self.width, self.height), 0, 24)

        # ombre en bas du menu
        self.surfo1 = pygame.Surface((self.width-self.taille_ombre, self.taille_ombre), 0, 24)
        self.surfo1.set_alpha(160)
        self.surfo1.fill(0)

        # ombre a droite du menu
        self.surfo2 = pygame.Surface((self.taille_ombre, self.height), 0, 24)
        self.surfo2.set_alpha(160)
        self.surfo2.fill(0)

        # Surface de la selection active 
        self.selecta = pygame.Surface((self.surf.get_width()-4, self.select_size))
        self.selecta.fill((221, 236, 255))

        #  Cadre de la surface de la selection
        pygame.draw.rect(self.selecta, (38, 160, 218), 
            (0, 0, *self.selecta.get_size()), width=1)

        # Surface de la selection inactive 
        self.selecti = pygame.Surface((self.surf.get_width()-4, self.select_size))
        self.selecti.fill(3*(238,))

        #  Cadre de la surface de la selection
        pygame.draw.rect(self.selecti, 3*(128,), 
            (0, 0, *self.selecti.get_size()), width=1)

    def get_nb_actions(self) -> int:
        return len(list(filter(lambda x: x.etat != "separateur", self.liste_actions)))

    def get_nb_separateurs(self) -> int:
        return len(list(filter(lambda x: x.etat == "separateur", self.liste_actions)))

    def get_position_from_index(self, index: int) -> int:
        pos_y: int = 2
        for idx, action in enumerate(self.liste_actions):
            if idx == index:
                return pos_y

            if action.etat == "separateur":
                pos_y += 2*self.border_size + 1
            else:
                pos_y += self.select_size

        return -1

    def get_index(self, pos_y: int) -> int:
        max_y: int = 0
        for idx, action in enumerate(self.liste_actions):
            if action.etat == "separateur":
                max_y += 2*self.border_size + 1
            else:
                max_y += self.select_size

            if pos_y < max_y:
                return idx

        return idx

    def activate(self, mouse_pos: tuple[int, int]):
        # fprint("activate Menu")

        # Ferme les potentiels Menu et Sous-menus deja ouverts
        self.close()

        self.animation = True
        self.alpha = 16

        # recalcul de la position par rapport aux bords de la fenetre
        pos_init: list[int] = list(mouse_pos)
        if mouse_pos[0] + self.surf.get_width() > self.screen.get_width():
            pos_init[0] = self.screen.get_width() - self.surf.get_width() - self.taille_ombre

        if mouse_pos[1] + self.surf.get_height() > self.screen.get_height():
            pos_init[1] = self.screen.get_height() - self.surf.get_height() - self.taille_ombre

        self.pos_init = pos_init[0], pos_init[1]
        self.show = True
        self.index = -1
        self.selected_index = -1
        self.old_index = -1
        self.time_for_action = 0

        if self.parent:
            self.parent.opened_sub_menu = self

    def draw(self, mouse_pos) -> None:
        if not self.is_open() or len(self.liste_actions) == 0:
            # Menu non ouvert ou vide
            return

        # remplissage de la couleur de fond du menu
        self.surf.fill((240, 240, 240))

        # Animation d'ouverture du menu
        if self.animation:
            # fprint("Menu.animation")
            self.alpha += 32
            if self.alpha >= 255:
                self.animation = False
                self.surf.set_alpha(255)
            else:
                self.surf.set_alpha(self.alpha)

        # Bords du menu
        pygame.draw.rect(self.surf, 3*(151,), self.surf.get_rect(), width=1)

        # ligne vertical a gauche separant icone & texte
        pygame.draw.line(self.surf, 3*(191,), (self.goutiere_size, 2), (30, self.surf.get_height()-3))

        # recherche de l'element selectionne dans le menu
        if (self.border_size < mouse_pos[1] < self.surf.get_height()-self.border_size and 
                self.surf.get_rect().collidepoint(mouse_pos)):

            # 
            # ToDo : a deplacer pour prendre en compte le sous-menu
            # 
            self.index = self.get_index(mouse_pos[1])
            self.selected_index = self.index
        else:
            # Aucun element de selectionne dans le menu
            self.index = -1

        if self.selected_index > -1 and self.opened_sub_menu or self.index > -1:
            select_position = self.get_position_from_index(self.selected_index)

            match self.liste_actions[self.selected_index].etat:
                case "actif":
                    self.surf.blit(self.selecta, (2, select_position))
                case "inactif":
                    self.surf.blit(self.selecti, (2, select_position))

        # gestion de l'ouverture/fermeture automatique des sous-menus
        if self.index != self.old_index:

            if (self.index == -1 and self.old_index >= 0 and 
                    self.liste_actions[self.old_index].sub_menu and
                    self.liste_actions[self.old_index].sub_menu.is_open()):
                # Force la selection du Sous-Menu
                # self.index = self.old_index
                pass
            else:
                self.old_index = self.index
                
            if (self.liste_actions[self.index].sub_menu and 
                    not self.liste_actions[self.index].sub_menu.is_open()):
                # Mise a jour du timer pour l'ouverture auto
                self.time_for_action = 20

            elif self.is_sub_menu_open() and self.time_for_action == 0:
                # Mise a jour du timer pour la fermeture auto
                self.time_for_action = 20

        else:
            # Gestion du timer pour les actions auto
            if self.time_for_action == 1:
                # Action automatique a executer
                self.time_for_action = 0
                if self.liste_actions[self.index].sub_menu:
                    if not self.liste_actions[self.index].sub_menu.is_open():
                        # Ouverture du sub_menu et fermeture du precedent si besoin
                        self.close_sub_menu()
                        self.click()

                elif self.is_sub_menu_open():
                    self.close_sub_menu()

            elif self.time_for_action > 0:
                self.time_for_action -= 1

        dy: int = self.border_size
        for idx, action in enumerate(self.liste_actions):
            if action.etat == "actif":
                couleur = (0, 0, 0)
            else:
                couleur = (132, 109, 155)

            # Calcul de la position du libelle du menu a afficher
            lib = self.font24.render(action.libelle, True, couleur)
            _, height = lib.get_size()
            if action.etat == "separateur":
                dy += self.border_size 

                # separateur horizontal
                pygame.draw.line(
                    self.surf, 
                    3*(191,), 
                    (self.goutiere_size, dy), 
                    (self.width-3, dy))

                dy += self.border_size + 1
                continue
            else:
                dy += self.select_size

            # Ajout du libelle a la position calculee
            self.surf.blit(lib, (6+self.goutiere_size, dy-(self.select_size+height)//2))

            if action.raccourci:
                # Affichage du raccourci si existant
                if action.sub_menu:
                    rac = self.fontsymbole.render(u"\u276F", True, couleur)
                else:
                    rac = self.font24.render(action.raccourci, True, couleur)

                width, height = rac.get_size()
                # Ajout du raccourci a la position calculee
                self.surf.blit(rac, 
                    (self.surf.get_width()-16-width, 
                     dy-(self.select_size+height)//2))
            
        # Ajout de la surface du menu + les 2 ombres (bas et droite)
        self.screen.blits(
            ((self.surf, self.pos_init),
            (self.surfo1, 
                (self.pos_init[0]+self.taille_ombre, self.pos_init[1]+self.surf.get_height())),
            (self.surfo2, 
                (self.pos_init[0]+self.surf.get_width(), self.taille_ombre+self.pos_init[1]))))

        # Affichage du sous-menu ouvert si besoin
        if self.opened_sub_menu:
            new_mouse_pos: tuple = Mouse.get_diff(self.opened_sub_menu.pos_init)
            self.opened_sub_menu.draw(new_mouse_pos)

        return

    def click(self):
        result: str = ""
        # fprint(f"{self.titre}({self.index})", self.liste_actions[self.index].etat, end="")
        if self.index < 0 and self.opened_sub_menu and self.opened_sub_menu.selected_index > -1:
            # fprint(" > ", end="")
            result = self.opened_sub_menu.click()
        # fprint(f"#{self.titre}({result})")

        # fprint(self.titre, ", After Submenu() result:", result, " selectedidx:", self.selected_index)
        if result in ("", "OUT") and self.index > -1:
            # fprint(f"1-{self.titre}({self.index})")
            if self.liste_actions[self.index].etat in ["inactif", "separateur"]:
                # fprint(self.titre, ", Return INSEP")
                return "INSEP"

            # fprint(f"2-{self.titre}({self.index})", self.liste_actions[self.index].raccourci)
            if self.liste_actions[self.index].is_sub_menu():
                # Sous-menu
                # fprint(f"3-{self.titre}({self.index})")
                if self.liste_actions[self.index].sub_menu.is_open():
                    # fprint(self.titre, ", Return OPEN")
                    return "OPEN"

                # fprint(f"5-{self.titre}({self.index}) (activate submenu)")
                dx, dy = self.pos_init
                self.liste_actions[self.index].sub_menu.activate(
                    (dx+self.surf.get_width()-8, 
                     dy+self.get_position_from_index(self.index)))

                # fprint(self.titre, ", Return Activate")
                return "ACTIVATE"

            else:
                result = "CLOSE"
        else:
            if result == "" and self.index < 0:
                if self.parent:
                    # fprint(self.titre, ", Result OUT")
                    result = "OUT"
                else:
                    # fprint(self.titre, ", Result Close")
                    result = "CLOSE"

        # fprint(self.titre, ", Result before close():", result, " selectedidx:", self.selected_index)
        if result == "CLOSE":
            self.close()

        if self.index < 0:
            if self.opened_sub_menu is None:
                # fprint(f"6-{self.titre}({self.index}|{self.selected_index}) (CLOSE)")
                return "CLOSE"

            # fprint(self.titre, ", Return empty")
            return result

        # fprint(f"7-{self.titre}({self.index}) (FUNCTION?)")
        action = self.liste_actions[self.index]
        if action.fonction:
            action.fonction()

        # fprint(f"8-{self.titre}({self.index}|{self.selected_index}) (CLOSE)")
        return "CLOSE"

    def print_espion(self):
        for action in self.liste_actions:
            fprint(action.libelle, end="")
            if action.sub_menu:
                fprint(f"IsOpen({action.sub_menu.is_open()})", end="")
            fprint()

    def contains(self, position) -> bool:
        return self.surf.get_rect().collidepoint(position)

    def is_open(self) -> bool:
        return self.show

    def is_sub_menu_open(self) -> bool:
        for action in self.liste_actions:
            if action.sub_menu and action.sub_menu.is_open():
                return True

        return False

    def close_sub_menu(self):
        for action in self.liste_actions:
            if action.sub_menu and action.sub_menu.is_open():
                action.sub_menu.close()

    def close(self):
        if not self.is_open():
            return 

        self.show = False
        if self.parent:
            self.parent.opened_sub_menu = None

        for action in self.liste_actions:
            if action.sub_menu and action.sub_menu.is_open():
                action.sub_menu.close()


def end_run():
    Variable.Running = False


def bloc_bleu(menu) -> None:
    if Variable.Menu == "bleu":
        return

    menu.close()

    menu_lvl3 = Menu("SsMenuBleuLvl3")
    menu_lvl3.add(Action("Sous menu 31", "", "actif", fprint, "Sous menu 31"))
    menu_lvl3.add(Action("Sous menu 32", "", "actif", fprint, "Sous menu 32"))
    menu_lvl3.add(Action("Sous menu 33", "", "actif", fprint, "Sous menu 33"))
    menu_lvl3.add(Action("", "", "separateur"))
    menu_lvl3.add(Action("Fermer", "Ctrl-W", "actif", toggle, "bleu"))
    menu_lvl3.compute()

    sub_menu1 = Menu("SsMenuBleu1")
    sub_menu1.add(Action("Sous menu 11", "", "actif", fprint, "Sous menu 11"))
    sub_menu1.add(Action("Sous menu 12", "", "actif", fprint, "Sous menu 12"))
    sub_menu1.add(Action("Sous menu 13", "", "actif", fprint, "Sous menu 13"))
    sub_menu1.add(Action("", "", "separateur"))
    sub_menu1.add(Action("Sous menu 14", "", "actif", fprint, "Sous menu 14"))
    sub_menu1.add(Action("Gestion du fenetrage", ">", "actif", menu_lvl3))
    sub_menu1.add(Action("Sous menu 16", "", "actif", fprint, "Sous menu 15"))
    sub_menu1.add(Action("Sous menu 17", "", "actif", fprint, "Sous menu 16"))
    sub_menu1.add(Action("", "", "separateur"))
    sub_menu1.add(Action("Sous menu 18", "", "actif", fprint, "Sous menu 17"))
    sub_menu1.add(Action("Sous menu 19", "", "actif", fprint, "Sous menu 18"))
    sub_menu1.add(Action("Sous menu 20", "", "actif", fprint, "Sous menu 19"))
    sub_menu1.add(Action("", "", "separateur"))
    sub_menu1.add(Action("Fermer", "Ctrl-W", "actif", toggle, "bleu"))
    sub_menu1.compute()

    sub_menu2 = Menu("SsMenuBleu2")
    sub_menu2.add(Action("Sous menu 21", "", "actif", fprint, "Sous menu 21"))
    sub_menu2.add(Action("Sous menu 22", "", "actif", fprint, "Sous menu 22"))
    sub_menu2.add(Action("Sous menu 23", "", "actif", fprint, "Sous menu 23"))
    sub_menu2.add(Action("", "", "separateur"))
    sub_menu2.add(Action("Sous menu 24", "", "actif", fprint, "Sous menu 24"))
    sub_menu2.add(Action("Sous menu 25", "", "actif", fprint, "Sous menu 25"))
    sub_menu2.add(Action("Sous menu 26", "", "actif", fprint, "Sous menu 26"))
    sub_menu2.add(Action("Sous menu 27", "", "actif", fprint, "Sous menu 27"))
    sub_menu2.add(Action("", "", "separateur"))
    sub_menu2.add(Action("Fermer", "Ctrl-W", "actif", toggle, "bleu"))
    sub_menu2.compute()

    menu.clear()
    if Variable.taille["bleu"]:
        menu.add(Action("Minimiser", "", "actif", minimizeRestaure, "bleu"))
    else:
        menu.add(Action("Restaurer", "", "actif", minimizeRestaure, "bleu"))
    menu.add(Action("Go to Definition(Jedi)", "Ctrl+Shift+G", "actif"))
    menu.add(Action("Find usage (Jedi)", "Alt+Shift+F", "actif"))
    menu.add(Action("Show Docstring (Jedi)", "Ctrl+Alt+D", "actif"))
    menu.add(Action("Show signature", "", "actif"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Show Diff Hunk", "", "actif"))
    menu.add(Action("Revert Diff Hunk", "", "actif"))
    menu.add(Action("Show Unsaved Changed", "", "inactif"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Cut", "Ctrl+X", "actif"))
    menu.add(Action("Copy", "Ctrl+C", "actif"))
    menu.add(Action("Paste", "Ctrl+V", "actif"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Select All", "Ctrl+A", "actif"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Open Containing Folder", "", "actif"))
    menu.add(Action("Copy File Path", ">", "actif", sub_menu1))
    menu.add(Action("Reveal in Side Bar", "", "actif"))
    menu.add(Action("Behave Toolkit", ">", "actif", sub_menu2))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Fermer", "Ctrl-W", "actif", toggle, "bleu"))

    menu.compute()
    Variable.Menu = "bleu"


def bloc_blanc(menu) -> None:
    if Variable.Menu == "blanc":
        return

    menu.clear()

    restaure: str = "inactif" if Variable.taille["blanc"] else "actif"
    minimize: str = "actif" if Variable.taille["blanc"] else "inactif"

    menu.add(Action("Restaurer", "", restaure, minimizeRestaure, "blanc"))
    menu.add(Action("Minimiser", "", minimize, minimizeRestaure, "blanc"))

    menu.add(Action("Déplacer", "", "inactif"))
    menu.add(Action("Taille", "", "actif"))
    menu.add(Action("Réduire", "", "actif"))
    menu.add(Action("Agrandir", "", "actif", fprint, "Agridissement"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Fermer", "Ctrl-W", "actif", toggle, "blanc"))

    menu.compute()
    Variable.Menu = "blanc"


def bloc_rouge(menu) -> None:
    if Variable.Menu == "rouge":
        return

    menu.clear()

    restaure: str = "inactif" if Variable.taille["rouge"] else "actif"
    minimize: str = "actif" if Variable.taille["rouge"] else "inactif"

    menu.add(Action("Restaurer", "", restaure, minimizeRestaure, "rouge"))
    menu.add(Action("Minimiser", "", minimize, minimizeRestaure, "rouge"))

    menu.add(Action("Déplacer", "", "actif"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Fermer", "Ctrl-W", "actif", toggle, "rouge"))

    menu.compute()
    Variable.Menu = "rouge"


def bloc_vert(menu) -> None:
    if Variable.Menu == "vert":
        return

    menu.clear()
    restaure: str = "inactif" if Variable.taille["vert"] else "actif"
    minimize: str = "actif" if Variable.taille["vert"] else "inactif"

    menu.add(Action("Restaurer", "", restaure, minimizeRestaure, "vert"))
    menu.add(Action("Minimiser", "", minimize, minimizeRestaure, "vert"))

    menu.add(Action("Déplacer", "", "actif"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Fermer", "", "actif", toggle, "vert"))

    menu.compute()
    Variable.Menu = "vert"


def no_bloc(menu) -> None:
    if Variable.Menu == "aucun":
        return

    reduire_tout: bool = False
    restaurer_tout: bool = False
    separateur: bool = False

    menu.clear()
    nb_fermer: int = 0
    if not Variable.Bleu:
        menu.add(Action("Ouvrir Bleu", "", "actif", toggle, "bleu"))
        separateur = True
        nb_fermer += 1
    else:
        reduire_tout = Variable.taille.get("bleu", 0) == 1
        restaurer_tout = Variable.taille.get("bleu", 0) == 0

    if not Variable.Blanc:
        menu.add(Action("Ouvrir Blanc", "", "actif", toggle, "blanc"))
        separateur = True
        nb_fermer += 1
    else:
        reduire_tout = reduire_tout or Variable.taille.get("blanc", 0) == 1
        restaurer_tout = restaurer_tout or Variable.taille.get("blanc", 0) == 0

    if not Variable.Rouge:
        menu.add(Action("Ouvrir Rouge", "", "actif", toggle, "rouge"))
        separateur = True
        nb_fermer += 1
    else:
        reduire_tout = reduire_tout or Variable.taille.get("rouge", 0) == 1
        restaurer_tout = restaurer_tout or Variable.taille.get("rouge", 0) == 0

    if not Variable.Vert:
        menu.add(Action("Ouvrir Vert", "", "actif", toggle, "vert"))
        separateur = True
        nb_fermer += 1
    else:
        reduire_tout = reduire_tout or Variable.taille.get("vert", 0) == 1
        restaurer_tout = restaurer_tout or Variable.taille.get("vert", 0) == 0

    if reduire_tout:
        menu.add(Action("Réduire Tout", "", "actif", minimizeRestaure, "reduire"))

    if restaurer_tout:
        menu.add(Action("Restaurer Tout", "", "actif", minimizeRestaure, "restaure"))

    if separateur:
        menu.add(Action("", "", "separateur"))

    if separateur:
        menu.add(Action("Ouvrir Tout", "", "actif", toggle, "open"))
    if nb_fermer != 4:
        menu.add(Action("Fermer Tout", "Ctrl+Shift+w", "actif", toggle, "close"))

    menu.add(Action("", "", "separateur"))
    menu.add(Action("Quitter", "Alt-F4", "actif", end_run))

    menu.compute()
    Variable.Menu = "aucun"


def minimizeRestaure(couleur: str) -> None:
    if couleur == "reduire":
        # force l'affichage minimal des objets
        for color in Variable.taille:
            Variable.taille[color] = 0

    elif couleur == "restaure":
        # force l'affichage complet des objets
        for color in Variable.taille:
            Variable.taille[color] = 1

    else:
        Variable.taille[couleur] = 1 - Variable.taille.get(couleur, 1)

    # Force la mise a jour du Menu même si on ne change pas le curseur souris d'objet
    Variable.Menu = ""


def toggle(couleur: str) -> None:

    Variable.Menu = ""
    match couleur.lower():
        case "bleu":
            Variable.Bleu = not Variable.Bleu
        case "blanc":
            Variable.Blanc = not Variable.Blanc
        case "rouge":
            Variable.Rouge = not Variable.Rouge
        case "vert":
            Variable.Vert = not Variable.Vert
        case "open":
            Variable.Bleu = True
            Variable.Blanc = True
            Variable.Vert = True
            Variable.Rouge = True
        case "close":
            Variable.Bleu = False
            Variable.Blanc = False
            Variable.Vert = False
            Variable.Rouge = False


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1360, 820), flags=pygame.RESIZABLE + pygame.SRCALPHA)

    Menu.init(screen)
    menu = Menu("Menu")
    no_bloc(menu)

    screen_size = screen.get_rect()
    clock = pygame.time.Clock()

    while Variable.Running:
        clock.tick(60)

        if screen_size != screen.get_rect():
            screen_size = screen.get_rect()
            print(screen_size)

        screen.fill((50, 150, 100))

        if Variable.Bleu:
            if Variable.taille.get("bleu", 0):
                posy, dy = 200, 400
            else:
                posy, dy = 780, 30
            bleu = pygame.draw.rect(screen, "blue", (100, posy, 250, dy))

        if Variable.Blanc:
            if Variable.taille.get("blanc", 0):
                posy, dy = 200, 300
            else:
                posy, dy = 780, 30
            blanc = pygame.draw.rect(screen, "white", (400, posy, 250, dy))

        if Variable.Rouge:
            if Variable.taille.get("rouge", 0):
                posy, dy = 200, 300
            else:
                posy, dy = 780, 30
            rouge = pygame.draw.rect(screen, "red", (700, posy, 250, dy))

        if Variable.Vert:
            if Variable.taille.get("vert", 0):
                posy, dy = 200, 300
            else:
                posy, dy = 780, 30
            vert = pygame.draw.rect(screen, "green", (1000, posy, 300, dy))

        menu.draw(Mouse.get_diff(menu.pos_init))
        pygame.display.update()

        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                Variable.Running = False        

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if menu.is_open():
                        menu.close()
                    else:
                        Variable.Running = False

            elif event.type in [pygame.KEYUP, pygame.TEXTINPUT, pygame.TEXTEDITING]:
                pass

            elif event.type == pygame.MOUSEMOTION:
                Mouse.set_pos(*event.pos)

            elif event.type in [pygame.MOUSEBUTTONUP]:

                if menu.is_open() and (event.button == 1 or 
                        menu.contains(Mouse.get_diff(menu.pos_init))):
                    # fprint("\nMouse.click()")
                    menu.click()

                elif event.button == 3:
                    if Variable.Bleu and bleu.collidepoint(Mouse.get_pos()):
                        bloc_bleu(menu)
                    elif Variable.Blanc and blanc.collidepoint(Mouse.get_pos()):
                        bloc_blanc(menu)
                    elif Variable.Rouge and rouge.collidepoint(Mouse.get_pos()):
                        bloc_rouge(menu)
                    elif Variable.Vert and vert.collidepoint(Mouse.get_pos()):
                        bloc_vert(menu)
                    else:
                        no_bloc(menu)

                    menu.activate(Mouse.get_pos())

            elif event.type in [pygame.MOUSEBUTTONDOWN]:
                pass

            elif event.type in [pygame.MOUSEWHEEL]:
                pass

            elif event.type in [pygame.WINDOWFOCUSGAINED, pygame.WINDOWFOCUSLOST, pygame.WINDOWSHOWN]:
                pass

            elif event.type in [pygame.WINDOWENTER, pygame.WINDOWLEAVE, pygame.WINDOWEXPOSED]:
                pass

            elif event.type in [pygame.VIDEOEXPOSE, pygame.VIDEORESIZE]:
                pass

            elif event.type in [pygame.WINDOWMINIMIZED, pygame.WINDOWRESTORED]:
                pass

            elif event.type == pygame.JOYDEVICEADDED:
                pass

            elif event.type == pygame.AUDIODEVICEADDED:
                pass

            elif event.type == pygame.ACTIVEEVENT:
                pass

            else:
                fprint(event)
                
    pygame.quit()


if __name__ == '__main__':
    main()
