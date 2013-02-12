#include "histo.hpp"
#include <iostream>

using namespace hist;
using namespace std;

Histo::Histo(int numlatbins,int numlonbins,int num_datapts,int *lat_index,int *lon_index)
{
  numlats=numlatbins;
  numlons=numlonbins;
  num_data=num_datapts;
  grid_length=numlats*numlons;
  lat_index_ptr=lat_index;
  lon_index_ptr=lon_index;
  int grid_row,grid_col,oned_index;
  for(int i =0; i< numlats; i++){
    for(int j=0; j < numlons; j++) {
      outvec.push_back(std::vector<int>());
    }
  } 
  for(int i=0;i < num_data;i++){
    grid_row=lat_index[i];
    grid_col=lon_index[i];
    if(grid_row < 0 || grid_col < 0) {
      continue;
    }
    oned_index=grid_row*numlons + grid_col;
    // if(oned_index > 0){
    //   std::cout << i << " " << grid_row << " " << grid_col  << " " << oned_index << std::endl;
    // }
    outvec[oned_index].push_back(i);
  }
}

std::vector<int> Histo::get_vec(int grid_row, int grid_col){
  int oned_index=grid_row*numlons + grid_col;
  std::vector<int> lat_lon=outvec[oned_index];
  return lat_lon;
}

void Histo::get_hist2d(int *hist2dout){
  int oned_index,cell_size;
  std::vector<int> latlon_cell;
  for(int grid_row =0; grid_row< numlats; grid_row++){
    for(int grid_col=0; grid_row < numlons; grid_col++) {
      oned_index=grid_row*numlons + grid_col;
      latlon_cell=outvec[oned_index];
      cell_size=latlon_cell.size();
      if(cell_size == 0){
	continue;
      }
      hist2dout[oned_index]=cell_size;
    }
  }
}

void Histo::get_mean(float *datain,float *meanout){
  std::vector<int> latlon_cell;
  std::vector<int>::iterator itr;
  for(int i=0;i < grid_length;i++){
    latlon_cell=outvec[i];
    int cell_size=latlon_cell.size();
    if(cell_size == 0){
      continue;
    }
    meanout[i]=0.;
    for (itr = latlon_cell.begin(); itr != latlon_cell.end(); ++itr ){
      meanout[i]=meanout[i] + datain[*itr];
    }
    meanout[i]=meanout[i]/cell_size;
  }
}


Histo::~Histo()
{
}
