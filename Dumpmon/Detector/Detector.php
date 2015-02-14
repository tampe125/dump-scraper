<?php

namespace Dumpmon\Detector;

abstract class Detector
{
    /** @var  float   Final score for the current file */
    protected $score;

    /** @var  string    Data that will be analyzed */
    protected $data;

    /** @var  integer   The number of lines of the file */
    protected $lines;

    /**
     * Returns the score for the current file. High values results in a higher probability to belong to the current
     * class of analyzer
     *
     * @return float
     */
    public function getScore()
    {
        return $this->score;
    }

    /**
     * Resets all the internal pointers
     */
    public function reset()
    {
        $this->score = 0;
        $this->data  = '';
    }

    /**
     * Shorthand method to set all the features to the class
     *
     * @param array $features
     */
    public function setInfo(array $features = array())
    {
        foreach($features as $feature => $value)
        {
            if(property_exists($this, $feature))
            {
                $this->$feature = $value;
            }
        }
    }

    /**
     * Entry point for analyzing the file
     *
     * @param   array   $results    Indexed array containing the results of other Detectors
     *
     * @return void
     */
    public abstract function analyze($results);
}
