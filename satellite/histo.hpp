#include <vector>

namespace hist {
  class Histo {
  public:
    int numlats;
    int numlons;
    int grid_length;
    int num_data;
    int *lat_index_ptr;
    int *lon_index_ptr;
    std::vector< std::vector<int> > outvec;
    std::vector<int> get_vec(int row, int col);
    void get_mean(float *datain,float *meanout);
    void get_hist2d(int *histout);
    Histo(int numlatbins,int numlonbins,int num_datapts,int *lat_index,int *lon_index);
    ~Histo();
  };
}
