#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define PIXEL(ptr, x, y) \
      (*(uint32_t*)((ptr) + (y) * (STRIDE) + (x) * 4))
#define PIXEL_PUT(ptr, x, y, color) \
      (*((uint32_t*)((ptr) + ((x) + (y) * WIDTH) * 4)) = (uint32_t)(color))
void
paint_border(uint8_t* ptr, int WIDTH, int HEIGHT, int STRIDE)
{
  uint8_t* newptr = malloc(STRIDE*HEIGHT*sizeof(uint8_t));
  memcpy(newptr, ptr, STRIDE*HEIGHT);
  for (int i = 0; i < WIDTH; ++i)
    for (int j = 0; j < HEIGHT; ++j) 
    {
      uint32_t color = PIXEL(ptr, i, j);
      uint32_t up = (j-1 >= 0) ? PIXEL(ptr, i, j-1): color;
      uint32_t right = (i-1 >= 0) ? PIXEL(ptr, i-1, j): color;
      uint32_t left = (i+1 < WIDTH) ? PIXEL(ptr, i+1, j): color;
      uint32_t down = (j+1 < HEIGHT) ? PIXEL(ptr, i, j+1): color;
      if (up != color || down != color || left != color || right != color)
        PIXEL_PUT(newptr, i, j, 0xFF000000);
      else
        PIXEL_PUT(newptr, i, j, 0xFFFFFFFF);
    }
  memmove(ptr, newptr, STRIDE*HEIGHT);
  free(newptr);
}
