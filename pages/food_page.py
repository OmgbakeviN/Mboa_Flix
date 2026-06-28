import tkinter as tk
from PIL import Image, ImageDraw, ImageTk, ImageFilter

from config import COLORS, ASSETS_DIR, BASE_DIR
from components.navbar import Navbar

try:
    from services.food_service import load_foods
except ImportError:
    load_foods = None


DEFAULT_FOODS = [
    {
        "id": "food_001",
        "name": "Ndolé",
        "region": "Littoral / Cameroon",
        "image": "assets/foods/ndole.png",
        "short_description": "A famous Cameroonian dish made with bitter leaves, peanuts, meat or fish.",
        "description": "Ndolé is one of the most popular dishes in Cameroon. It is prepared with bitter leaves, groundnuts, spices and usually served with meat, fish or shrimps. This dish is often eaten during family events and important celebrations.",
        "ingredients": ["Bitter leaves", "Groundnuts", "Beef", "Fish", "Shrimps"],
        "served_with": "Plantains, rice, miondo or bobolo"
    },
    {
        "id": "food_002",
        "name": "Poulet DG",
        "region": "Urban Cameroon",
        "image": "assets/foods/poulet_dg.png",
        "short_description": "A festive dish with chicken, fried plantains, vegetables and spices.",
        "description": "Poulet DG is a festive Cameroonian dish often associated with special guests and celebrations. It is made with chicken, fried plantains, carrots, green beans, peppers and spices.",
        "ingredients": ["Chicken", "Plantains", "Carrots", "Green beans", "Pepper"],
        "served_with": "Fried plantains and vegetables"
    },
    {
        "id": "food_003",
        "name": "Eru",
        "region": "South West Cameroon",
        "image": "assets/foods/eru.png",
        "short_description": "A traditional meal made with eru leaves, waterleaf, palm oil, meat and fish.",
        "description": "Eru is a traditional dish from the South West region of Cameroon. It is made with eru leaves, waterleaf, palm oil, meat, fish and sometimes cow skin. It is usually served with water fufu or garri.",
        "ingredients": ["Eru leaves", "Waterleaf", "Palm oil", "Meat", "Fish"],
        "served_with": "Water fufu or garri"
    },
    {
        "id": "food_004",
        "name": "Achu Soup",
        "region": "North West Cameroon",
        "image": "assets/foods/achu_soup.png",
        "short_description": "A yellow soup served with pounded cocoyam, loved in the grassfields.",
        "description": "Achu Soup is a traditional dish from the North West region of Cameroon. It is known for its yellow soup made with palm oil, limestone water, spices and meat.",
        "ingredients": ["Cocoyam", "Palm oil", "Limestone water", "Meat", "Spices"],
        "served_with": "Pounded cocoyam"
    },
    {
        "id": "food_005",
        "name": "Koki",
        "region": "West / Littoral Cameroon",
        "image": "assets/foods/koki.png",
        "short_description": "A steamed bean cake made with palm oil and eaten with ripe plantains.",
        "description": "Koki is a delicious Cameroonian dish made from crushed beans mixed with red palm oil and spices. It is wrapped in leaves and steamed until firm.",
        "ingredients": ["Koki beans", "Palm oil", "Pepper", "Salt", "Leaves"],
        "served_with": "Ripe plantains"
    },
    {
        "id": "food_006",
        "name": "Roasted Fish",
        "region": "Coastal Cameroon",
        "image": "assets/foods/roasted_fish.png",
        "short_description": "A street food classic served with miondo, plantains and pepper sauce.",
        "description": "Roasted Fish is one of the most loved street foods in Cameroon. The fish is seasoned, grilled and served with pepper sauce, onions, plantains or miondo.",
        "ingredients": ["Fresh fish", "Pepper", "Onions", "Spices", "Oil"],
        "served_with": "Miondo, plantains or bobolo"
    }
]


class FoodPage(tk.Frame):
    def __init__(
        self,
        master,
        user=None,
        on_home=None,
        on_food=None,
        on_about=None,
        on_logout=None
    ):
        super().__init__(master, bg=COLORS["background"])

        self.user = user or {}
        self.on_home = on_home
        self.on_food = on_food
        self.on_about = on_about
        self.on_logout = on_logout

        self.foods = self._load_food_data()

        self.background_original = self._load_background()
        self.background_photo = None
        self.card_photos = {}
        self.detail_photo = None
        self.detail_bg_photo = None
        self.resize_after_id = None
        self.detail_modal = None

        self.bg_item = None
        self.content_window = None

        self.pack(fill="both", expand=True)

        self._build_ui()
        self.after(120, self._render_background)

    def _load_food_data(self):
        if load_foods:
            try:
                foods = load_foods()
                if foods:
                    return foods
            except Exception:
                pass

        return DEFAULT_FOODS

    def _build_ui(self):
        self.navbar = Navbar(
            self,
            user=self.user,
            on_search=None,
            on_logout=self.on_logout,
            on_home=self.on_home,
            on_food=self.on_food,
            on_about=self.on_about,
            active_page="food"
        )
        self.navbar.place(x=0, y=0, relwidth=1, height=82)

        self.canvas = tk.Canvas(
            self,
            bg="#000000",
            highlightthickness=0,
            bd=0
        )
        self.canvas.place(
            x=0,
            y=82,
            relwidth=1,
            relheight=1,
            height=-82
        )

        self.bg_item = self.canvas.create_image(
            0,
            0,
            anchor="nw"
        )

        self.scrollbar = tk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )
        self.scrollbar.place(
            relx=1.0,
            x=-12,
            y=82,
            width=12,
            relheight=1.0,
            height=-82
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content = tk.Frame(
            self.canvas,
            bg="#050505",
            highlightbackground="#242424",
            highlightthickness=1
        )

        self.content_window = self.canvas.create_window(
            70,
            55,
            window=self.content,
            anchor="nw",
            width=1120
        )

        self._build_content()

        self.content.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

    def _build_content(self):
        header = tk.Frame(self.content, bg="#050505")
        header.pack(fill="x", padx=48, pady=(45, 35))

        title = tk.Label(
            header,
            text="Cameroonian Food",
            bg="#050505",
            fg=COLORS["text"],
            font=("Arial", 38, "bold"),
            anchor="w"
        )
        title.pack(fill="x")

        subtitle = tk.Label(
            header,
            text=(
                "Discover six iconic dishes from Cameroon. "
                "Click on a card to learn more about the dish, its origin and how it is usually served."
            ),
            bg="#050505",
            fg=COLORS["muted"],
            font=("Arial", 13),
            wraplength=850,
            justify="left",
            anchor="w"
        )
        subtitle.pack(fill="x", pady=(12, 0))

        grid = tk.Frame(self.content, bg="#050505")
        grid.pack(fill="x", padx=34, pady=(0, 55))

        for index, food in enumerate(self.foods[:6]):
            card = self._create_food_card(grid, food)

            row = index // 3
            column = index % 3

            card.grid(
                row=row,
                column=column,
                padx=14,
                pady=18,
                sticky="n"
            )

        for column in range(3):
            grid.grid_columnconfigure(column, weight=1)

    def _create_food_card(self, master, food):
        card_width = 300
        card_height = 430

        card = tk.Frame(
            master,
            bg="#111111",
            width=card_width,
            height=card_height,
            highlightbackground="#303030",
            highlightthickness=1,
            cursor="hand2"
        )
        card.pack_propagate(False)

        image = self._load_food_image(food, card_width, 255)
        photo = ImageTk.PhotoImage(image)
        self.card_photos[food.get("id", food.get("name", "food"))] = photo

        image_label = tk.Label(
            card,
            image=photo,
            bg="#111111",
            bd=0,
            cursor="hand2"
        )
        image_label.pack(fill="x")

        info = tk.Frame(card, bg="#111111", cursor="hand2")
        info.pack(fill="both", expand=True, padx=18, pady=16)

        name = tk.Label(
            info,
            text=food.get("name", "Food"),
            bg="#111111",
            fg=COLORS["text"],
            font=("Arial", 18, "bold"),
            anchor="w",
            cursor="hand2"
        )
        name.pack(fill="x")

        region = tk.Label(
            info,
            text=food.get("region", ""),
            bg="#111111",
            fg=COLORS["primary"],
            font=("Arial", 10, "bold"),
            anchor="w",
            cursor="hand2"
        )
        region.pack(fill="x", pady=(5, 12))

        short_description = tk.Label(
            info,
            text=food.get("short_description", ""),
            bg="#111111",
            fg=COLORS["muted"],
            font=("Arial", 10),
            wraplength=255,
            justify="left",
            anchor="w",
            cursor="hand2"
        )
        short_description.pack(fill="x")

        more = tk.Label(
            info,
            text="Click to read more →",
            bg="#111111",
            fg=COLORS["text"],
            font=("Arial", 10, "bold"),
            anchor="w",
            cursor="hand2"
        )
        more.pack(fill="x", side="bottom", pady=(10, 0))

        self._bind_card_events(card, food, card)

        return card

    def _bind_card_events(self, widget, food, card):
        widget.bind("<Button-1>", lambda event: self._open_food_detail(food))
        widget.bind("<Enter>", lambda event: self._on_card_hover(card))
        widget.bind("<Leave>", lambda event: self._on_card_leave(card))

        for child in widget.winfo_children():
            self._bind_card_events(child, food, card)

    def _on_card_hover(self, card):
        card.configure(
            highlightbackground=COLORS["primary"],
            highlightthickness=2
        )

    def _on_card_leave(self, card):
        card.configure(
            highlightbackground="#303030",
            highlightthickness=1
        )

    def _open_food_detail(self, food):
        if self.detail_modal:
            self.detail_modal.destroy()

        self.detail_modal = tk.Frame(self, bg="#000000")
        self.detail_modal.place(
            x=0,
            y=82,
            relwidth=1,
            relheight=1,
            height=-82
        )
        self.detail_modal.lift()

        bg_label = tk.Label(self.detail_modal, bd=0)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        width = max(self.winfo_width(), 900)
        height = max(self.winfo_height() - 82, 580)

        bg_image = self._load_food_image(food, width, height)
        bg_image = bg_image.filter(ImageFilter.GaussianBlur(radius=12))

        dark = Image.new("RGB", bg_image.size, "#000000")
        bg_image = Image.blend(bg_image, dark, 0.68)

        self.detail_bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label.config(image=self.detail_bg_photo)

        panel = tk.Frame(
            self.detail_modal,
            bg="#0b0b0b",
            highlightbackground="#333333",
            highlightthickness=1
        )
        panel.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=940,
            height=510
        )

        close_button = tk.Button(
            panel,
            text="← Back to Food",
            command=self._close_food_detail,
            bg="#1d1d1d",
            fg=COLORS["text"],
            activebackground="#2a2a2a",
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 11, "bold"),
            padx=16,
            pady=8
        )
        close_button.place(x=24, y=22)

        image = self._load_food_image(food, 310, 390)
        self.detail_photo = ImageTk.PhotoImage(image)

        image_label = tk.Label(
            panel,
            image=self.detail_photo,
            bg="#111111",
            bd=0
        )
        image_label.place(x=34, y=90, width=310, height=390)

        info = tk.Frame(panel, bg="#0b0b0b")
        info.place(x=390, y=88, width=500, height=390)

        region = tk.Label(
            info,
            text=food.get("region", "").upper(),
            bg="#0b0b0b",
            fg=COLORS["primary"],
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        region.pack(fill="x")

        title = tk.Label(
            info,
            text=food.get("name", "Food"),
            bg="#0b0b0b",
            fg=COLORS["text"],
            font=("Arial", 34, "bold"),
            anchor="w"
        )
        title.pack(fill="x", pady=(8, 16))

        description = tk.Label(
            info,
            text=food.get("description", ""),
            bg="#0b0b0b",
            fg=COLORS["text"],
            font=("Arial", 12),
            wraplength=490,
            justify="left",
            anchor="w"
        )
        description.pack(fill="x", pady=(0, 18))

        served = tk.Label(
            info,
            text=f"Served with: {food.get('served_with', 'N/A')}",
            bg="#0b0b0b",
            fg=COLORS["muted"],
            font=("Arial", 11, "bold"),
            wraplength=490,
            justify="left",
            anchor="w"
        )
        served.pack(fill="x", pady=(0, 14))

        ingredients_title = tk.Label(
            info,
            text="Main ingredients",
            bg="#0b0b0b",
            fg=COLORS["text"],
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        ingredients_title.pack(fill="x", pady=(0, 8))

        tags = tk.Frame(info, bg="#0b0b0b")
        tags.pack(fill="x")

        for ingredient in food.get("ingredients", []):
            tag = tk.Label(
                tags,
                text=ingredient,
                bg="#1d1d1d",
                fg=COLORS["text"],
                font=("Arial", 9, "bold"),
                padx=10,
                pady=5
            )
            tag.pack(side="left", padx=(0, 7), pady=(0, 7))

    def _close_food_detail(self):
        if self.detail_modal:
            self.detail_modal.destroy()
            self.detail_modal = None

    def _load_food_image(self, food, width, height):
        path_value = food.get("image", "")
        path = BASE_DIR / path_value if path_value else None

        if path and path.exists():
            image = Image.open(path).convert("RGB")
        else:
            image = self._placeholder_food_image(
                food.get("name", "Food"),
                width,
                height
            )

        return self._cover_image(image, width, height)

    def _placeholder_food_image(self, title, width, height):
        image = Image.new("RGB", (width, height), "#1a1a1a")
        draw = ImageDraw.Draw(image)

        for y in range(height):
            ratio = y / max(height - 1, 1)
            r = int(55 * (1 - ratio) + 12 * ratio)
            g = int(30 * (1 - ratio) + 10 * ratio)
            b = int(12 * (1 - ratio) + 8 * ratio)
            draw.line((0, y, width, y), fill=(r, g, b))

        draw.rectangle((0, height - 90, width, height), fill="#070707")
        draw.text((20, 20), "MBOA FLIX FOOD", fill="#E50914")
        draw.text((20, height - 58), title[:28], fill="white")

        return image

    def _load_background(self):
        path = ASSETS_DIR / "food_background.png"

        if path.exists():
            return Image.open(path).convert("RGB")

        return Image.new("RGB", (1100, 680), "#120804")

    def _render_background(self):
        width = max(self.canvas.winfo_width(), 900)
        height = max(self.canvas.winfo_height(), 580)

        image = self._cover_image(self.background_original, width, height)

        dark = Image.new("RGB", image.size, "#000000")
        image = Image.blend(image, dark, 0.35)

        self.background_photo = ImageTk.PhotoImage(image)

        self.canvas.itemconfig(
            self.bg_item,
            image=self.background_photo
        )

        self.canvas.coords(
            self.bg_item,
            0,
            self.canvas.canvasy(0)
        )

        self.canvas.tag_lower(self.bg_item)

    def _cover_image(self, image, width, height):
        image_ratio = image.width / image.height
        target_ratio = width / height

        if target_ratio > image_ratio:
            new_width = width
            new_height = int(width / image_ratio)
        else:
            new_height = height
            new_width = int(height * image_ratio)

        resized = image.resize(
            (new_width, new_height),
            Image.LANCZOS
        )

        left = (new_width - width) // 2
        top = (new_height - height) // 2

        return resized.crop(
            (left, top, left + width, top + height)
        )

    def _update_scroll_region(self, _event=None):
        bbox = self.canvas.bbox("all")

        if bbox:
            self.canvas.configure(
                scrollregion=(0, 0, bbox[2], bbox[3] + 80)
            )

        self.canvas.tag_lower(self.bg_item)

    def _on_canvas_resize(self, event):
        content_width = max(event.width - 140, 960)

        self.canvas.itemconfig(
            self.content_window,
            width=content_width
        )

        self._render_background()

    def _on_mousewheel(self, event):
        if getattr(event, "num", None) == 4:
            self.canvas.yview_scroll(-3, "units")
        elif getattr(event, "num", None) == 5:
            self.canvas.yview_scroll(3, "units")
        else:
            self.canvas.yview_scroll(
                int(-1 * (event.delta / 120)) * 3,
                "units"
            )

        self._render_background()

        return "break"