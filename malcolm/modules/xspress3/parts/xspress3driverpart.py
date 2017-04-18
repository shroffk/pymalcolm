from malcolm.controllers.scanning.runnablecontroller import RunnableController, configure_args
from malcolm.core import method_takes
from malcolm.parts.ADCore.detectordriverpart import DetectorDriverPart


XSPRESS3_BUFFER = 16384


class Xspress3DriverPart(DetectorDriverPart):
    @RunnableController.Configure
    @RunnableController.PostRunReady
    @RunnableController.Seek
    @method_takes(*configure_args)
    def configure(self, context, completed_steps, steps_to_do, part_info, params):
        if steps_to_do > XSPRESS3_BUFFER:
            # Set the PointsPerRow from the innermost dimension
            gen_num = params.generator.dimensions[-1].size
            steps_per_row = XSPRESS3_BUFFER // gen_num * gen_num
        else:
            steps_per_row = steps_to_do
        child = context.block_view(self.params.mri)
        child.pointsPerRow.put_value(steps_per_row)
        child.triggerMode.put_value("Hardware")
        super(Xspress3DriverPart, self).configure(
            context, completed_steps, steps_to_do, part_info, params)