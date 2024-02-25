import pygame

from typing import Callable
from functools import partial


# for font in pygame.font.get_fonts():
#     if "seg" in font:
#         print(font)
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
    pos_init: tuple[int, ...]

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

        self.clear()

    @classmethod
    def clear(self) -> None:
        self.width = self.min_width
        self.liste_actions = []

    @classmethod
    def add(self, action: Action) -> None:
        action.set_index(len(self.liste_actions))
        self.liste_actions.append(action)

        lib = self.font24.render(f"{action.libelle}", True, (0, 0, 0))
        rac = self.font24.render(f"{action.raccourci}", True, (0, 0, 0))
        width_lib, _ = lib.get_size()
        width_rac, _ = rac.get_size()

        new_width: int = 6+self.goutiere_size + self.border_size + 10 + width_lib + width_rac + 16
        if new_width > self.width:
            self.width = new_width

    @classmethod
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

    @classmethod
    def get_nb_actions(self) -> int:
        return len(list(filter(lambda x: x.etat != "separateur", self.liste_actions)))

    @classmethod
    def get_nb_separateurs(self) -> int:
        return len(list(filter(lambda x: x.etat == "separateur", self.liste_actions)))

    @classmethod
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

    @classmethod
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

    @classmethod
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

        self.pos_init = tuple(pos_init)
        Mouse.set_pos(*self.pos_init)
        self.show = True
        self.index = -1

    @classmethod
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

    @classmethod
    def click(self):
        # fprint(self.index, "clicked")
        if self.index > -1:
            if self.liste_actions[self.index].etat in ["inactif", "separateur"]:
                return

        self.close()

        if self.index < 0:
            return

        action = self.liste_actions[self.index]
        if action.fonction:
            action.fonction()

    @classmethod
    def contains(self, position) -> bool:
        return self.surf.get_rect().collidepoint(position)

    @classmethod
    def is_open(self):
        return self.show

    @classmethod
    def close(self):
        self.show = False


def end_run():
    Variable.Running = False


def bloc_bleu():
    if Variable.Menu == "bleu":
        return

    Menu.clear()
    Menu.add(Action("Go to Definition (Jedi)", "Ctrl+Shift+G", "actif"))
    Menu.add(Action("Find usage (Jedi)", "Alt+Shift+F", "actif"))
    Menu.add(Action("Show Docstring (Jedi)", "Ctrl+Alt+D", "actif"))
    Menu.add(Action("Show signature", "", "actif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Show Diff Hunk", "", "actif"))
    Menu.add(Action("Revert Diff Hunk", "", "actif"))
    Menu.add(Action("Show Unsaved Changed", "", "inactif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Cut", "", "actif"))
    Menu.add(Action("Copy", "", "actif"))
    Menu.add(Action("Paste", "", "actif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Select All", "", "actif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Open Containing Folder", "", "actif"))
    Menu.add(Action("Copy File Path", "", "actif"))
    Menu.add(Action("Reveal in Side Bar", "", "actif"))
    # Menu.add(Action("Behave Toolkit", ">", "actif"))
    Menu.add(Action("Behave Toolkit", ">", "actif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Fermer", "Ctrl-w", "actif", toggle, "bleu"))
    Menu.add(Action("Quitter", "Alt-F4", "actif", end_run))

    Menu.compute()
    Variable.Menu = "bleu"


def bloc_blanc():
    if Variable.Menu == "blanc":
        return

    Menu.clear()
    Menu.add(Action("Restaurer", "", "inactif"))
    Menu.add(Action("Déplacer", "", "inactif"))
    Menu.add(Action("Taille", "", "actif"))
    Menu.add(Action("Réduire", "", "actif"))
    Menu.add(Action("Agrandir", "", "actif", print, "Agridissement"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Fermer", "Ctrl-w", "actif", toggle, "blanc"))

    Menu.compute()
    Variable.Menu = "blanc"


def bloc_rouge():
    if Variable.Menu == "rouge":
        return

    Menu.clear()
    Menu.add(Action("Restaurer", "", "inactif"))
    Menu.add(Action("Déplacer", "", "actif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Fermer", "Ctrl-w", "actif", toggle, "rouge"))

    Menu.compute()
    Variable.Menu = "rouge"


def bloc_vert():
    if Variable.Menu == "vert":
        return

    Menu.clear()
    Menu.add(Action("Show Unsaved Changes...", "", "actif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Cut", "Ctrl-X", "actif"))
    Menu.add(Action("Copy", "Ctrl-C", "actif"))
    Menu.add(Action("Paste", "Ctrl+V", "actif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Select All", "Ctrl+A", "actif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Open Git Repository...", "", "actif"))
    Menu.add(Action("File History...", "", "actif"))
    Menu.add(Action("Line History...", "", "actif"))
    Menu.add(Action("Blame File...", "", "actif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Open Containing mother fucking Folder", "Cmd+x", "actif"))
    Menu.add(Action("Copy File Path", "", "actif"))
    Menu.add(Action("Reveal in Side Bar", "", "actif"))
    Menu.add(Action("", "", "separateur"))
    Menu.add(Action("Fermer", "Ctrl-w", "actif", toggle, "vert"))

    Menu.compute()
    Variable.Menu = "vert"


def no_bloc():
    if Variable.Menu == "aucun":
        return
    separateur: bool = False
    Menu.clear()
    if not Variable.Bleu:
        Menu.add(Action("Ouvrir Bleu", "", "actif", toggle, "bleu"))
        separateur = True
    if not Variable.Blanc:
        Menu.add(Action("Ouvrir Blanc", "", "actif", toggle, "blanc"))
        separateur = True
    if not Variable.Rouge:
        Menu.add(Action("Ouvrir Rouge", "", "actif", toggle, "rouge"))
        separateur = True
    if not Variable.Vert:
        Menu.add(Action("Ouvrir Vert", "", "actif", toggle, "vert"))
        separateur = True

    if separateur:
        Menu.add(Action("", "", "separateur"))

    Menu.add(Action("Quitter", "Alt-F4", "actif", end_run))

    Menu.compute()
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


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1360, 820), flags=pygame.RESIZABLE + pygame.SRCALPHA)

    Menu.init(screen)
    Menu.add(Action("Fermer", "Ctrl-w", "actif", end_run))
    Menu.add(Action("Quitter", "Alt-F4", "actif", end_run))
    Menu.compute()

    screen_size: pygame.Rect = screen.get_rect()
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
            rect = pygame.Rect(100, 200, 250, 400)
            pygame.draw.rect(screen, "black", rect.move(5, 5))
            bleu = pygame.draw.rect(screen, "blue", rect)
        if Variable.Blanc:
            rect = pygame.Rect(400, 200, 250, 300)
            pygame.draw.rect(screen, "black", rect.move(5, 5))
            blanc = pygame.draw.rect(screen, "white", rect)
        if Variable.Rouge:
            rect = pygame.Rect(700, 200, 250, 300)
            pygame.draw.rect(screen, "black", rect.move(5, 5))
            rouge = pygame.draw.rect(screen, "red", rect)
        if Variable.Vert:
            rect = pygame.Rect(1000, 200, 300, 300)
            pygame.draw.rect(screen, "black", rect.move(5, 5))
            vert = pygame.draw.rect(screen, "green", rect)

        Menu.draw(Mouse.get_diff(pos_x, pos_y))
        pygame.display.update()

        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                Variable.Running = False        

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if Menu.is_open():
                        Menu.close()
                    else:
                        Variable.Running = False

            elif event.type in [pygame.KEYUP, pygame.TEXTINPUT, pygame.TEXTEDITING]:
                pass

            elif event.type == pygame.MOUSEMOTION:
                Mouse.set_pos(*event.pos)

            elif event.type in [pygame.MOUSEBUTTONUP]:

                if Menu.is_open() and (event.button == 1 or 
                        Menu.contains(Mouse.get_diff(pos_x, pos_y))):
                    Menu.click()

                elif event.button == 3:
                    if Variable.Bleu and bleu.collidepoint(Mouse.get_pos()):
                        bloc_bleu()
                    elif Variable.Blanc and blanc.collidepoint(Mouse.get_pos()):
                        bloc_blanc()
                    elif Variable.Rouge and rouge.collidepoint(Mouse.get_pos()):
                        bloc_rouge()
                    elif Variable.Vert and vert.collidepoint(Mouse.get_pos()):
                        bloc_vert()
                    else:
                        no_bloc()

                    Menu.activate(Mouse.get_pos())
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
