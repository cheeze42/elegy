with open("out.asm", 'w+') as asm_file:
    asm_file.write("""\
.device ATMega328P

.equ DDRB  = 0x04
.equ PORTB = 0x05
.equ DDRD  = 0x0a
.equ PORTD = 0x0b
.equ SPCR  = 0x2c
.equ SPSR  = 0x2d
.equ SPDR  = 0x2e

.equ DDB0 = 0
.equ DDB1 = 1
.equ DDB2 = 2
.equ DDB3 = 3
.equ DDB4 = 4
.equ DDB5 = 5
.equ DDB6 = 6
.equ DDB7 = 7

; SPCR - SPI Control Register
.equ SPR0 = 0 ; SPI Clock Rate Select 0
.equ SPR1 = 1 ; SPI Clock Rate Select 1
.equ CPHA = 2 ; Clock Phase
.equ CPOL = 3 ; Clock polarity
.equ MSTR = 4 ; Master/Slave Select
.equ DORD = 5 ; Data Order
.equ SPE  = 6 ; SPI Enable
.equ SPIE = 7 ; SPI Interrupt Enable

; SPSR - SPI Status Register
.equ SPI2X = 0 ; Double SPI Speed Bit
""")
    asm_file.write("\n")
    asm_file.write(".org 0x000\n")
    asm_file.write("  jmp main\n\n")
    asm_file.write("main:\n")
    asm_file.write("  clr r2\n")  # Using r2 to clear pixel output
    asm_file.write("  ser r19\n")  # Full register for outputs
    asm_file.write("  sbi DDRD, 0\n")  # Pin 0 for horizontal sync
    asm_file.write("  sbi DDRD, 1\n")  # Pin 1 for vertical sync
    # Both sync pulses have negative polarity
    asm_file.write("  sbi PORTD, 0\n")
    asm_file.write("  sbi PORTD, 1\n")
    # Set up SPI for pixel output
    asm_file.write("  ldi r16, (1<<DDB2)|(1<<DDB3)|(1<<DDB5)\n")
    asm_file.write("  out DDRB, r16\n")
    asm_file.write("  ldi r16, (1<<SPI2X)\n")
    asm_file.write("  out SPSR, r16\n")
    cpp = 2  # Cycles per pixel
    loop_time = 4  # How many cycles is our inner pixel loop?
    stretch = loop_time * cpp  # Total stretch factor
    
    # LOOP START
    asm_file.write("vga_loop:\n")

    # Last part of the previous frame
    for _ in range(128//cpp - 12):
        asm_file.write("  nop\n")

    # Pixel rows
    asm_file.write("  ldi r30, 0\n")  # Load base image pointer
    asm_file.write("  ldi r31, 0\n")
    asm_file.write(f"  ldi r16, {480//stretch}\n")  # Outer row counter
    asm_file.write(f"  ldi r17, {stretch}\n")
    asm_file.write("  lpm r18, Z+\n")  # Load the first pixel from memory
    asm_file.write("pixel_row_loop:\n")
    asm_file.write("pixel_row_inner:\n")
    # 640 pixel visible area
    # Enable SPI
    asm_file.write("  ldi r20, (1<<SPE)|(1<<MSTR)\n")
    asm_file.write("  out SPCR, r20\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    for _ in range(160//8 - 1):
        asm_file.write("  out SPDR, r19\n")  # Write the pixel out
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
        asm_file.write("  nop\n")
    asm_file.write("  ldi r20, (1<<MSTR)\n")
    asm_file.write("  out SPCR, r20\n")
    asm_file.write("  cbi PORTB, 3\n")
    # 24 pixel front porch
    for _ in range(24//cpp - 4):
        asm_file.write("  nop\n")
    # 40 pixel sync pulse
    asm_file.write("  cbi PORTD, 0\n")  # Start the horizontal pulse
    for _ in range(40//cpp - 2):
        asm_file.write("  nop\n")
    # 128 pixel back porch
    asm_file.write("  sbi PORTD, 0\n")  # Stop the horizontal pulse
    for _ in range(128//cpp - 14):
        asm_file.write("  nop\n")
    asm_file.write("  dec r17\n")
    asm_file.write("  breq pixel_row_inner_done\n")
    asm_file.write(f"  subi r30, low({640//stretch})\n")
    asm_file.write(f"  sbci r31, high({640//stretch})\n")
    asm_file.write("  lpm r18, Z+\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  jmp pixel_row_inner\n")
    asm_file.write("pixel_row_inner_done:\n")
    asm_file.write(f"  ldi r17, {stretch}\n")
    asm_file.write("  dec r16\n")
    asm_file.write("  breq pixel_row_loop_done\n")
    asm_file.write("  lpm r18, Z+\n")
    asm_file.write("  jmp pixel_row_loop\n")
    asm_file.write("pixel_row_loop_done:\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")

    # Vertical front porch
    asm_file.write("  ldi r16, 24\n")
    asm_file.write("vertical_front_porch_loop:\n")
    # 640 pixel visible area + 24 pixel front porch
    for _ in range(640//cpp + 24//cpp):
        asm_file.write("  nop\n")
    # 40 pixel sync pulse
    asm_file.write("  cbi PORTD, 0\n")  # Start the horizontal pulse
    for _ in range(40//cpp - 2):
        asm_file.write("  nop\n")
    # 128 pixel back porch
    asm_file.write("  sbi PORTD, 0\n")  # Stop the horizontal pulse
    for _ in range(128//cpp - 7):
        asm_file.write("  nop\n")
    asm_file.write("  dec r16\n")
    asm_file.write("  breq vertical_front_porch_loop_done\n")
    asm_file.write("  jmp vertical_front_porch_loop\n")
    asm_file.write("vertical_front_porch_loop_done:\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")

    # Vertical sync
    for row_idx in range(2):
        # 640 pixel visible area + 24 pixel front porch
        if row_idx == 0:
            asm_file.write("  cbi PORTD, 1\n")  # Start the vertical pulse
        else:
            asm_file.write("  nop\n")
            asm_file.write("  nop\n")
        for _ in range(640//cpp + 24//cpp - 2):
            asm_file.write("  nop\n")
        # 40 pixel horizontal sync pulse
        asm_file.write("  cbi PORTD, 0\n")  # Start the horizontal pulse
        for _ in range(40//cpp - 2):
            asm_file.write("  nop\n")
        # 128 pixel back porch
        asm_file.write("  sbi PORTD, 0\n")  # Stop the horizontal pulse
        for _ in range(128//cpp - 3):
            asm_file.write("  nop\n")
        if row_idx == 0:
            asm_file.write("  nop\n")
        else:
            asm_file.write("  ldi r16, 28\n")
   
    # Vertical back porch, 29 lines total
    # Lines 0 - 28
    asm_file.write("  sbi PORTD, 1\n")  # Stop the vertical pulse
    asm_file.write("  vertical_back_porch_loop:\n")
    # 640 pixel visible area + 24 pixel front porch
    for _ in range(640//cpp + 24//cpp - 2):
        asm_file.write("  nop\n")
    # 40 pixel sync pulse
    asm_file.write("  cbi PORTD, 0\n")  # Start the horizontal pulse
    for _ in range(40//cpp - 2):
        asm_file.write("  nop\n")
    # 128 pixel back porch
    asm_file.write("  sbi PORTD, 0\n")  # Stop the horizontal pulse
    for _ in range(128//cpp - 7):
        asm_file.write("  nop\n")
    asm_file.write("  dec r16\n")
    asm_file.write("  breq vertical_back_porch_loop_done\n")
    asm_file.write("  nop\n")
    asm_file.write("  nop\n")
    asm_file.write("  jmp vertical_back_porch_loop\n")
    asm_file.write("vertical_back_porch_loop_done:\n")

    # Line 28
    # 640 pixel visible area + 24 pixel front porch
    for _ in range(640//cpp + 24//cpp + 2):
        asm_file.write("  nop\n")
    # 40 pixel sync pulse
    asm_file.write("  cbi PORTD, 0\n")  # Start the horizontal pulse
    for _ in range(40//cpp - 2):
        asm_file.write("  nop\n")
    # 128 pixel back porch
    asm_file.write("  sbi PORTD, 0\n")  # Stop the horizontal pulse
    asm_file.write("  jmp vga_loop\n")  # Restart the loop
