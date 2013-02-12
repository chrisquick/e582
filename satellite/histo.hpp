#include <vector>

namespace hist {
  class Histo {
  public:
    float* indata;
    Histo(float* indata);
    ~Histo();
    std::vector< std::vector<int> > outvec;
  };
}
