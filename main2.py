import pygame

from typing import Callable
from functools import partial


class Variable:
    Running = True
    Menu: str = ""
    Bleu: bool = True
    Blanc: bool = True
    Rouge: bool = True
    Vert: bool = True


class Mouse:
    pos_x: int = 0
    pos_y: int = 0

    @classmethod
    def set_pos(self, x: int, y: int) -> None:
        Mouse.pos_x = x
        Mouse.pos_y = y

    @classmethod
    def get_pos(self) -> tuple[int, int]:
        return Mouse.pos_x, Mouse.pos_y

    @classmethod
    def get_diff(self, x: int, y: int) -> tuple[int, int]:
        return Mouse.pos_x - x, Mouse.pos_y - y


def fprint(*args, **kwargs):
    print(*args, **kwargs, flush=True)


class Action:
    index: int
    libelle: str
    raccourci: str
    etat: str
    fonction: Callable

    def __init__(self, 
            libelle: str,
            raccourci: str,
            etat: str,
            fonction=None,
            *args, 
            **kwargs):

        self.libelle = libelle
        self.raccourci = raccourci
        self.etat = etat.lower()
        if args:
            part1 = partial(fonction, *args)
        else:
            part1 = fonction

        if kwargs:
            self.fonction = partial(part1, **kwargs)
        else:
            self.fonction = part1

    def __str__(self):
        return f"{self.libelle!r} {self.raccourci!r} {self.etat}"

    def set_index(self, index: int):
        self.index = index

    def exec(self):
        if self.fonction:
            self.fonction(*self.args, **self.kwargs)


class Menu:
    liste_actions: list[Action]

    screen: pygame.Surface
    surf: pygame.Surface 
    surfo1: pygame.Surface 
    surfo2: pygame.Surface
    selecta: pygame.Surface
    selecti: pygame.Surface

    font24: pygame.font.Font
    fontsymbole: pygame.font.Font
    pos_init: tuple[int, int]

    show: bool = False
    animation: bool = False

    index: int = -1

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

    def __init__(self):
        self.clear()

    def clear(self) -> None:
        self.width = self.min_width
        self.liste_actions = []

    def add(self, action: Action) -> None:
        action.set_index(len(self.liste_actions))
        self.liste_actions.append(action)

        lib = self.font24.render(f"{action.libelle}", True, (0, 0, 0))
        rac = self.font24.render(f"{action.raccourci}", True, (0, 0, 0))
        width_lib, height = lib.get_size()
        width_rac, height = rac.get_size()

        new_width: int
        if action.raccourci:
            new_width = 6+3*self.goutiere_size + self.border_size + 10 + width_lib + width_rac 
        else:
            new_width = 6+self.goutiere_size + self.border_size + 10 + width_lib + 16
        if new_width > self.width:
            self.width = new_width

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
        self.surfo1.set_alpha(96)
        self.surfo1.fill(0)

        # ombre a droite du menu
        self.surfo2 = pygame.Surface((self.taille_ombre, self.height), 0, 24)
        self.surfo2.set_alpha(96)
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
        self.animation = True
        self.alpha = 16

        # recalcul de la position par rapport aux bords de la fenetre
        pos_init: list[int] = list(mouse_pos)
        if mouse_pos[0] + self.surf.get_width() > self.screen.get_width():
            pos_init[0] = self.screen.get_width() - self.surf.get_width() - self.taille_ombre

        if mouse_pos[1] + self.surf.get_height() > self.screen.get_height():
            pos_init[1] = self.screen.get_height() - self.surf.get_height() - self.taille_ombre

        self.pos_init = pos_init[0], pos_init[1]
        Mouse.set_pos(*self.pos_init)
        self.show = True
        self.index = -1

    def draw(self, mouse_pos):
        if not self.show or len(self.liste_actions) == 0:
            return

        self.surf.fill((240, 240, 240))

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

        # ligne vertical separant icone & texte
        pygame.draw.line(self.surf, 3*(191,), (self.goutiere_size, 2), (30, self.surf.get_height()-3))

        if (self.border_size < mouse_pos[1] < self.surf.get_height()-self.border_size and 
                self.surf.get_rect().collidepoint(mouse_pos)):

            self.index = self.get_index(mouse_pos[1])
            select_position = self.get_position_from_index(self.index)

            match self.liste_actions[self.index].etat:
                case "separateur":
                    pass
                case "inactif":
                    self.surf.blit(self.selecti, (2, select_position))
                case _:
                    self.surf.blit(self.selecta, (2, select_position))
        else:
            self.index = -1

        dy: int = self.border_size
        for idx, action in enumerate(self.liste_actions):
            if action.etat == "actif":
                couleur = (0, 0, 0)
            else:
                couleur = (132, 109, 155)

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

            self.surf.blit(lib, (6+self.goutiere_size, dy-(self.select_size+height)//2))

            if action.raccourci:
                if action.raccourci == ">":
                    rac = self.fontsymbole.render(u"\u276F", True, couleur)
                else:
                    rac = self.font24.render(action.raccourci, True, couleur)
                width, height = rac.get_size()
                self.surf.blit(rac, 
                    (self.surf.get_width()-16-width, 
                        dy-(self.select_size+height)//2))
            
        self.screen.blits(
            ((self.surf, self.pos_init),
            (self.surfo1, 
            (self.pos_init[0]+self.taille_ombre, self.pos_init[1]+self.surf.get_height())),
            (self.surfo2, 
            (self.pos_init[0]+self.surf.get_width(), self.taille_ombre+self.pos_init[1]))))

    def click(self):
        
        if self.index > -1:
            if self.liste_actions[self.index].etat in ["inactif", "separateur"]:
                return

            if self.liste_actions[self.index].raccourci == ">":
                # ------------------------
                # ToDo Ouvrir le sous-Menu
                # ------------------------
                return

        self.close()

        if self.index < 0:
            return

        action = self.liste_actions[self.index]
        if action.fonction:
            action.fonction()

    def contains(self, position) -> bool:
        return self.surf.get_rect().collidepoint(position)

    def is_open(self):
        return self.show

    def close(self):
        self.show = False


def end_run():
    Variable.Running = False


def bloc_bleu(menu):
    if Variable.Menu == "bleu":
        return

    menu.clear()
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
    menu.add(Action("Copy File Path", "", "actif"))
    menu.add(Action("Reveal in Side Bar", "", "actif"))
    menu.add(Action("Behave Toolkit", ">", "actif"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Fermer", "Ctrl-W", "actif", toggle, "bleu"))

    menu.compute()
    Variable.Menu = "bleu"


def bloc_blanc(menu):
    if Variable.Menu == "blanc":
        return

    menu.clear()
    menu.add(Action("Restaurer", "", "inactif"))
    menu.add(Action("Déplacer", "", "inactif"))
    menu.add(Action("Taille", "", "actif"))
    menu.add(Action("Réduire", "", "actif"))
    menu.add(Action("Agrandir", "", "actif", print, "Agridissement"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Fermer", "Ctrl-W", "actif", toggle, "blanc"))

    menu.compute()
    Variable.Menu = "blanc"


def bloc_rouge(menu):
    if Variable.Menu == "rouge":
        return

    menu.clear()
    menu.add(Action("Restaurer", "", "inactif"))
    menu.add(Action("Déplacer", "", "actif"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Fermer", "Ctrl-W", "actif", toggle, "rouge"))

    menu.compute()
    Variable.Menu = "rouge"


def bloc_vert(menu):
    if Variable.Menu == "vert":
        return

    menu.clear()
    menu.add(Action("Restaurer", "", "inactif"))
    menu.add(Action("Déplacer", "", "actif"))
    menu.add(Action("", "", "separateur"))
    menu.add(Action("Fermer", "", "actif", toggle, "vert"))

    menu.compute()
    Variable.Menu = "vert"


def no_bloc(menu):
    if Variable.Menu == "aucun":
        return
    separateur: bool = False
    menu.clear()
    nb_fermer: int = 0
    if not Variable.Bleu:
        menu.add(Action("Ouvrir Bleu", "", "actif", toggle, "bleu"))
        separateur = True
        nb_fermer += 1
    if not Variable.Blanc:
        menu.add(Action("Ouvrir Blanc", "", "actif", toggle, "blanc"))
        separateur = True
        nb_fermer += 1
    if not Variable.Rouge:
        menu.add(Action("Ouvrir Rouge", "", "actif", toggle, "rouge"))
        separateur = True
        nb_fermer += 1
    if not Variable.Vert:
        menu.add(Action("Ouvrir Vert", "", "actif", toggle, "vert"))
        separateur = True
        nb_fermer += 1

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


def toggle(couleur: str):
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


def main():
    pygame.init()
    screen = pygame.display.set_mode((1360, 820), flags=pygame.RESIZABLE + pygame.SRCALPHA)

    Menu.init(screen)

    menu = Menu()
    menu.add(Action("Fermer", "Ctrl-w", "actif", end_run))
    menu.add(Action("Quitter", "Alt-F4", "actif", end_run))
    menu.compute()

    screen_size = screen.get_rect()
    clock = pygame.time.Clock()

    pos_x: int = 0
    pos_y: int = 0

    while Variable.Running:
        clock.tick(60)

        if screen_size != screen.get_rect():
            screen_size = screen.get_rect()
            print(screen_size)

        screen.fill((50, 150, 100))

        if Variable.Bleu:
            bleu = pygame.draw.rect(screen, "blue", (100, 200, 250, 400))
        if Variable.Blanc:
            blanc = pygame.draw.rect(screen, "white", (400, 200, 250, 300))
        if Variable.Rouge:
            rouge = pygame.draw.rect(screen, "red", (700, 200, 250, 300))
        if Variable.Vert:
            vert = pygame.draw.rect(screen, "green", (1000, 200, 300, 300))

        menu.draw(Mouse.get_diff(pos_x, pos_y))
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
                        menu.contains(Mouse.get_diff(pos_x, pos_y))):
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
                    pos_x, pos_y = Mouse.get_pos()

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
