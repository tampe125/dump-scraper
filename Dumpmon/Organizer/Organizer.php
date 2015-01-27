<?php

namespace Dumpmon\Organizer;

abstract class Organizer
{
    /** @var  float   Final score for the current file */
    protected $score;

    /** @var  string    Data that will be analyzed */
    protected $data;

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
     * @return void
     */
    public abstract function analyze();
}
