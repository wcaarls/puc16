#include "puc16.h"

unsigned char buf[] = "Hello, world!";

void main(void)
{
  for (char *cc=buf; *cc; ++cc)
  {
    while (inp(LDR));
    outp(*cc, LDR);
  }
}
