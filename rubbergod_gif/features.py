# Adapted GIF features for Tockar Discord Bot
# Original from RubberGod: https://github.com/vutfitdiscord/rubbergod/tree/main/cogs/gif

from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw

# Use images path relative to the project root
IMAGES_PATH = Path("rubbergod_gif/images")


class ImageHandler:
    """Image processing utilities for GIF generation."""
    
    @classmethod
    def square_to_circle(cls, image: Image.Image) -> Image.Image:
        """Convert a square image to a circular one with transparent background."""
        width, height = image.size
        mask = Image.new("L", (width, height), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, width, height), fill=255)
        alpha = image.getchannel("A") if image.mode == "RGBA" else None
        circle_alpha = Image.new("L", (width, height), 0)
        
        if alpha:
            circle_alpha.paste(alpha, mask=mask)
        else:
            circle_alpha = mask
            
        result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        result.paste(image, (0, 0), mask=circle_alpha)
        return result

    @classmethod
    def render_catnap(cls, image_binary: BytesIO, avatar: Image.Image, avatar_offset=(48, 12)):
        """Create catnap/steal animation with hopping motion."""
        speed = 60
        hop_size = 4
        frame_count = 11

        images_path = IMAGES_PATH / "cat_steal"

        try:
            background = Image.open(images_path / "catyay.png").convert("RGBA")
            catpaw = Image.open(images_path / "catpaw.png").convert("RGBA")
            
            # Create the initial composite image
            im = Image.new("RGBA", (150, 200), (0, 0, 0, 0))
            x, y = avatar_offset
            width, height = 150, 150
            
            im.paste(background, (38 // 2, 38 + 50), background)
            im.paste(avatar, (x, y + 50), avatar)
            im.paste(catpaw, (38 // 2, 38 + 50), catpaw)
            im2 = im.transpose(Image.FLIP_LEFT_RIGHT)

            frames = []
            
            # First direction (left to right)
            for i in range(frame_count):
                im = im.convert("RGBA")
                frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                hop = 12 if i % 2 else 12 + hop_size
                frame.paste(im, (i * 10 - 50, hop - 50), im)
                frames.append(frame)

            # Second direction (right to left)
            for i in range(frame_count):
                im2 = im2.convert("RGBA")
                frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                hop = 12 + hop_size if i % 2 else 12
                frame.paste(im2, ((10 - i) * 10 - 50, hop - 50), im2)
                frames.append(frame)

        except FileNotFoundError:
            # Fallback animation if images not found
            frames = []
            for i in range(20):
                frame = Image.new("RGBA", (150, 150), (0, 0, 0, 0))
                
                # Simple sliding motion
                if i < 10:
                    x_pos = i * 10
                else:
                    x_pos = 150 - ((i - 10) * 10)
                
                y_pos = 60 + (5 if i % 2 else 0)  # Small hop
                
                if 0 <= x_pos <= 150 - avatar.width:
                    frame.paste(avatar, (x_pos, y_pos), avatar)
                
                frames.append(frame)

        # Save as GIF
        frames[0].save(
            image_binary,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            duration=speed,
            loop=0,
            transparency=0,
            disposal=2,
            optimize=False,
        )
        image_binary.seek(0)

    @classmethod
    def get_bonk_frames(cls, avatar: Image.Image) -> list[Image.Image]:
        """Generate bonk animation frames using original RubberGod positioning."""
        frames = []
        width, height = 200, 170
        deformation = (0, 0, 0, 5, 10, 20, 15, 5)

        avatar = cls.square_to_circle(avatar.resize((100, 100)))
        images_path = IMAGES_PATH / "bonk"

        for i in range(8):
            try:
                img = "%02d" % (i + 1)
                frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                bat = Image.open(f"{images_path}/{img}.png").convert("RGBA")
                
                # Apply deformation to avatar
                deformed_avatar = avatar.resize((100, 100 - deformation[i]))
                frame_avatar = deformed_avatar.convert("P", palette=Image.Resampling.LANCZOS, colors=200).convert("RGBA")
                
                # Paste avatar at correct position with deformation offset
                frame.paste(frame_avatar, (80, 60 + deformation[i]), frame_avatar)
                # Paste bat on top
                frame.paste(bat, (10, 5), bat)
                frames.append(frame)
                
            except FileNotFoundError:
                # Fallback to simple animation if image not found
                frame = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                
                # Simple deformation as fallback
                deformed_avatar = avatar.resize((100, 100 - deformation[i]))
                frame_avatar = deformed_avatar.convert("P", palette=Image.Resampling.LANCZOS, colors=200).convert("RGBA")
                
                frame.paste(frame_avatar, (80, 60 + deformation[i]), frame_avatar)
                
                # Draw simple bat as fallback
                draw = ImageDraw.Draw(frame)
                draw.ellipse((10, 5, 50, 25), fill=(139, 69, 19))  # Brown bat
                
                frames.append(frame)

        return frames

    @classmethod  
    def get_pet_frames(cls, avatar: Image.Image) -> list[Image.Image]:
        """Generate pet animation frames."""
        frames = []
        deform_width = [-1, -2, 1, 2, 1]
        deform_height = [4, 3, 1, 1, -4]
        width, height = 80, 80
        x, y = 112, 122

        images_path = IMAGES_PATH / "pet"
        avatar = cls.square_to_circle(avatar)

        for i in range(5):
            frame = Image.new("RGBA", (x, y), (0, 0, 0, 0))
            
            try:
                hand = Image.open(f"{images_path}/{i}.png").convert("RGBA")
            except FileNotFoundError:
                # Fallback to simple hand drawing
                hand = Image.new("RGBA", (x, y), (0, 0, 0, 0))
                draw = ImageDraw.Draw(hand)
                # Simple hand shapes based on frame
                if i == 0:
                    draw.ellipse((15, 10, 45, 30), fill=(255, 220, 177, 200))
                elif i == 1:
                    draw.ellipse((15, 15, 45, 35), fill=(255, 220, 177, 200))
                elif i == 2:
                    draw.ellipse((15, 20, 45, 40), fill=(255, 220, 177, 200))
                elif i == 3:
                    draw.ellipse((15, 15, 45, 35), fill=(255, 220, 177, 200))
                else:
                    draw.ellipse((15, 10, 45, 30), fill=(255, 220, 177, 200))
            
            # Apply deformation
            current_width = width - deform_width[i]
            current_height = height - deform_height[i]
            deformed_avatar = avatar.resize((current_width, current_height))
            deformed_avatar = deformed_avatar.convert("P", palette=Image.Resampling.LANCZOS, colors=200).convert("RGBA")

            # Paste avatar and hand
            frame.paste(deformed_avatar, (x - current_width, y - current_height), deformed_avatar)
            frame.paste(hand, (0, 0), hand)
            frames.append(frame)

        return frames