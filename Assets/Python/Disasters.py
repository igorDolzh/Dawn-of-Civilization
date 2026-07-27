# Whether the natural disasters already in the game are allowed to fire.
#
# The mod ships thirteen weather and geological event triggers, and until now the only way to stop
# them was GAMEOPTION_NO_EVENTS, which also kills every beneficial, diplomatic and civ-spawn event.
# This module backs a dedicated setup-screen dropdown instead, so disasters can be turned off on
# their own.
#
# Nothing here adds a disaster. The triggers are wired to enabled() through their <PythonCanDo> tag
# in CIV4EventTriggerInfos.xml, and CvGame::doGlobalWarming consults the C++ half of the same
# contract, CvMap::areDisastersEnabled.

from Core import *


### THE OPTION ###

# Custom map option slot. Slot 0 is the scenario - CvMap::getScenario() reads getCustomMapOption(0)
# directly - so disasters take slot 1, declared in PrivateMaps/Dawn_of_Civilization.py.
iDisastersOption = 1

# Index of "Off" in lDisasters in that same file. CvMap::areDisastersEnabled hardcodes the same
# value; the two must agree.
iDisastersOff = 1


def enabled():
	"""Whether disasters may fire. Errs towards yes.

	This is called from CvRandomEventInterface, whose return value the DLL reads into an
	uninitialised local (CvPlayer::initTriggeredData). An exception escaping here would leave the
	DLL acting on undefined memory, so every failure path returns True instead - the worst case
	being the behaviour the mod already had.

	The option count is checked rather than assumed because saves made before the option existed
	carry only one custom map option.
	"""
	try:
		if map.getNumCustomMapOptions() <= iDisastersOption:
			return True

		return map.getCustomMapOption(iDisastersOption) != iDisastersOff
	except:
		return True
