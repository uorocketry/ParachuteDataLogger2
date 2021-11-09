#ifndef SCALES_H
#define SCALES_H

#include <board_comm.h>

namespace scales
{
    void init();
    void setPower(bool on);
    bool scalesReady();
    board_comm::Reading readOnce();
}

#endif
