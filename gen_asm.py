with open("out.asm", 'w+') as asm_file:
    asm_file.write(".device ATMega328P\n")
    asm_file.write(".equ DDRB = 0x04\n")
    asm_file.write(".equ PORTB = 0x05\n")
    asm_file.write(".equ DDRD = 0x0a\n")
    asm_file.write(".equ PORTD = 0x0b\n")
    asm_file.write("\n")
    asm_file.write(".org 0x000\n")
    asm_file.write("  jmp main\n\n")
    asm_file.write("main:\n")
    asm_file.write("  cbi DDRD, 0\n")  # Pins 0 for pixel output
    asm_file.write("  sbi DDRB, 0\n")  # Pin 8 for horizontal sync
    asm_file.write("  sbi DDRB, 1\n")  # Pin 9 for vertical sync
    # Both sync pulses have negative polarity
    asm_file.write("  sbi PORTB, 0\n")
    asm_file.write("  sbi PORTB, 1\n")
    cycles_per_pixel = 16
    asm_file.write(f"  ldi r18, {cycles_per_pixel}\n")  # Preparing the pixel row repetitions
    
    # LOOP START
    asm_file.write("vga_loop:\n")

    # Pixel rows
    cycles_per_pixel = 16
    for pixel_row_idx in range(480//cycles_per_pixel):
        asm_file.write(f"pixel_row_{pixel_row_idx}_loop:\n")
        # 640 pixel visible area
        for _ in range(640//8):
            asm_file.write("  sbi PORTD, 0\n")  # Write the pixel out
        # 24 pixel front porch
        asm_file.write("  cbi PORTD, 0\n")  # Clear pixel output
        for _ in range(24//4 - 1):
            asm_file.write("  nop\n")
        # 40 pixel sync pulse
        asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
        for _ in range(40//4 - 2):
            asm_file.write("  nop\n")
        # 128 pixel back porch
        asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
        for _ in range(128//4 - 7):
            asm_file.write("  nop\n")
        asm_file.write("  dec r18\n")
        asm_file.write(f"  breq pixel_row_{pixel_row_idx}_done\n")
        asm_file.write(f"  jmp pixel_row_{pixel_row_idx}_loop\n")
        asm_file.write(f"pixel_row_{pixel_row_idx}_done:\n")
        asm_file.write(f"  ldi r18, {cycles_per_pixel}\n")
        asm_file.write("  nop\n")
    
    # Vertical front porch
    for _ in range(24):
        # 640 pixel visible area + 24 pixel front porch
        for _ in range(640//4 + 24//4):
            asm_file.write("  nop\n")
        # 40 pixel sync pulse
        asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
        for _ in range(40//4 - 2):
            asm_file.write("  nop\n")
        # 128 pixel back porch
        asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
        for _ in range(128//4 - 2):
            asm_file.write("  nop\n")

    # Vertical sync
    for row_idx in range(2):
        # 640 pixel visible area + 24 pixel front porch
        if row_idx == 0:
            asm_file.write("  cbi PORTB, 1\n")  # Start the vertical pulse
        else:
            asm_file.write("  nop\n")
            asm_file.write("  nop\n")
        for _ in range(640//4 + 24//4 - 2):
            asm_file.write("  nop\n")
        # 40 pixel horizontal sync pulse
        asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
        for _ in range(40//4 - 2):
            asm_file.write("  nop\n")
        # 128 pixel back porch
        asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
        for _ in range(128//4 - 2):
            asm_file.write("  nop\n")
   
    # Vertical back porch, 29 lines total
    for row_idx in range(29):
        # 640 pixel visible area + 24 pixel front porch
        if row_idx == 0:
            asm_file.write("  sbi PORTB, 1\n")  # Stop the vertical pulse
        else:
            asm_file.write("  nop\n")
            asm_file.write("  nop\n")
        for _ in range(640//4 + 24//4 - 2):
            asm_file.write("  nop\n")
        # 40 pixel sync pulse
        asm_file.write("  cbi PORTB, 0\n")  # Start the horizontal pulse
        for _ in range(40//4 - 2):
            asm_file.write("  nop\n")
        # 128 pixel back porch
        asm_file.write("  sbi PORTB, 0\n")  # Stop the horizontal pulse
        for _ in range(128//4 - 2):
            asm_file.write("  nop\n")
