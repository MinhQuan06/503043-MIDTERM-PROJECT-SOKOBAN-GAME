from pathlib import Path

import pygame

from gui.button import Button
from gui.renderer import SokobanRenderer
from gui.screens.base_screen import BaseScreen

from source.task2_competitive.competitive_state import CompetitiveState


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MAP_DIR = PROJECT_ROOT / "maps"


class CompetitiveSetupScreen(BaseScreen):
    BACKGROUND = (24, 27, 32)
    PANEL = (34, 39, 47)
    BORDER = (78, 91, 108)
    TEXT = (240, 238, 225)
    MUTED = (165, 176, 190)
    ACCENT = (238, 164, 55)

    # Chỉ chọn các map có đủ A và X.
    MAPS = [
        ("Map 1", "competitive_map.txt"),  
        ("Map 2", "competitive_map2.txt"), 
        ("Map 3", "competitive_map3.txt"),
    ]

    def __init__(self, app):
        super().__init__(app)

        self.renderer = SokobanRenderer(tile_size=40)

        self.selected_map_index = 0
        self.preview_state = None
        self.message = ""

        # Số lượt mặc định
        self.turns_text = "100"
        self.input_active = False

        self.title_font = pygame.font.SysFont(
            "arial", 32, bold=True
        )
        self.font = pygame.font.SysFont(
            "arial", 20, bold=True
        )
        self.small_font = pygame.font.SysFont("arial", 16)

        self._build_layout()
        self._load_preview()

    def _build_layout(self):
        margin = 35
        gap = 20

        self.left_rect = pygame.Rect(
            margin, 115, 230, self.app.HEIGHT - 225
        )

        center_x = self.left_rect.right + gap
        center_width = (
            self.app.WIDTH - 2 * margin - 460 - 2 * gap
        )

        self.center_rect = pygame.Rect(
            center_x, 115,
            center_width, self.app.HEIGHT - 225
        )

        self.right_rect = pygame.Rect(
            self.center_rect.right + gap,
            115, 230, self.app.HEIGHT - 225
        )

        self.map_buttons = [
            Button(
                (
                    self.left_rect.x + 15,
                    185 + index * 70,
                    200,
                    50
                ),
                label,
                lambda index=index: self._select_map(index)
            )
            for index, (label, _) in enumerate(self.MAPS)
        ]

        self.turns_input_rect = pygame.Rect(
            self.right_rect.x + 20,
            240,
            self.right_rect.width - 40,
            50
        )

        self.back_button = Button(
            (35, self.app.HEIGHT - 80, 160, 50),
            "Back",
            self._go_back
        )

        self.start_button = Button(
            (
                self.app.WIDTH - 195,
                self.app.HEIGHT - 80,
                160,
                50
            ),
            "Start",
            self._start
        )

    def _select_map(self, index):
        self.selected_map_index = index
        self.message = ""
        self._load_preview()

    def _load_preview(self):
        _, filename = self.MAPS[self.selected_map_index]
        path = MAP_DIR / filename

        try:
            self.preview_state = CompetitiveState.from_file(
                str(path)
            )
            self.message = ""
        except (OSError, ValueError) as error:
            self.preview_state = None
            self.message = str(error)

    def _go_back(self):
        from gui.screens.menu_screen import MenuScreen

        self.app.change_screen(MenuScreen(self.app))

    def _start(self):
        if not self.turns_text:
            self.message = "Please enter max turns."
            return

        max_turns = int(self.turns_text)

        if max_turns < 1:
            self.message = "Max turns must be at least 1."
            return

        if self.preview_state is None:
            self.message = "Please select a valid map."
            return

        _, filename = self.MAPS[self.selected_map_index]

        self.app.selected_map = str(MAP_DIR / filename)
        self.app.selected_agent = 2
        self.app.max_turns = max_turns

        from gui.screens.competitive_game_screen import (
            CompetitiveGameScreen
        )

        self.app.change_screen(
            CompetitiveGameScreen(self.app)
        )

    def handle_event(self, event):
        for button in (
            self.map_buttons
            + [self.back_button, self.start_button]
        ):
            button.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.input_active = (
                    self.turns_input_rect.collidepoint(event.pos)
                )

        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.turns_text = self.turns_text[:-1]

            elif event.unicode.isascii() and event.unicode.isdigit():
                if len(self.turns_text) < 5:
                    self.turns_text += event.unicode

    def _draw_panel(self, surface, rect, title):
        pygame.draw.rect(
            surface, self.PANEL, rect, border_radius=10
        )

        pygame.draw.rect(
            surface, self.BORDER, rect,
            width=2, border_radius=10
        )

        image = self.font.render(title, True, self.TEXT)

        surface.blit(
            image,
            image.get_rect(
                midtop=(rect.centerx, rect.y + 18)
            )
        )

    def draw(self, surface):
        surface.fill(self.BACKGROUND)

        title = self.title_font.render(
            "SOKOBAN - COMPETITIVE",
            True,
            self.ACCENT
        )

        surface.blit(
            title,
            title.get_rect(
                center=(self.app.WIDTH // 2, 55)
            )
        )

        self._draw_panel(
            surface, self.left_rect, "SELECT MAP"
        )
        self._draw_panel(
            surface, self.center_rect, "MAP PREVIEW"
        )
        self._draw_panel(
            surface, self.right_rect, "GAME SETTINGS"
        )

        for index, button in enumerate(self.map_buttons):
            button.draw(surface)

            if index == self.selected_map_index:
                pygame.draw.rect(
                    surface, self.ACCENT,
                    button.rect, width=3,
                    border_radius=10
                )

        preview_area = pygame.Rect(
            self.center_rect.x + 12,
            self.center_rect.y + 65,
            self.center_rect.width - 24,
            self.center_rect.height - 125
        )

        pygame.draw.rect(
            surface, (18, 21, 25),
            preview_area, border_radius=8
        )

        if self.preview_state is not None:
            self.renderer.render_competitive_state(
                surface,
                self.preview_state,
                preview_area
            )

        label = self.small_font.render(
            "Max turns (n):",
            True, self.TEXT
        )

        surface.blit(
            label,
            (
                self.right_rect.x + 20,
                self.turns_input_rect.y - 30
            )
        )

        border_color = (
            self.ACCENT if self.input_active else self.BORDER
        )

        pygame.draw.rect(
            surface, (18, 21, 25),
            self.turns_input_rect,
            border_radius=8
        )

        pygame.draw.rect(
            surface, border_color,
            self.turns_input_rect,
            width=2, border_radius=8
        )

        value = self.font.render(
            self.turns_text, True, self.TEXT
        )

        surface.blit(
            value,
            (
                self.turns_input_rect.x + 12,
                self.turns_input_rect.y + 12
            )
        )

        agent1 = self.small_font.render(
            "Agent 1: A*",
            True, self.TEXT
        )
        agent2 = self.small_font.render(
            "Agent 2: GBFS",
            True, self.TEXT
        )

        surface.blit(
            agent1,
            (self.right_rect.x + 20, 330)
        )
        surface.blit(
            agent2,
            (self.right_rect.x + 20, 365)
        )

        self.back_button.draw(surface)
        self.start_button.draw(surface)

        if self.message:
            message_image = self.small_font.render(
                self.message,
                True, self.ACCENT
            )

            surface.blit(
                message_image,
                message_image.get_rect(
                    center=(
                        self.app.WIDTH // 2,
                        self.app.HEIGHT - 105
                    )
                )
            )